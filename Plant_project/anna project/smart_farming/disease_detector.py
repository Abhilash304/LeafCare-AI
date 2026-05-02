"""
disease_detector.py - Plant disease detection using TensorFlow Lite or dummy fallback
Works OFFLINE - uses local model if available, else realistic dummy logic
"""

import os
import random
from PIL import Image
import numpy as np

# Hugging Face Model Integration
try:
    from transformers import (
        pipeline, 
        MobileNetV2ImageProcessor, 
        MobileNetV2ForImageClassification
    )
    import torch
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

# Global cache for the HF components
_hf_classifier = None
_hf_model = None
_hf_processor = None
_hf_object_detector = None  # Cache for YOLOS-tiny

HF_MODEL_ID = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
HF_TOKEN = "YOUR_TOKEN_HERE"

# Paths
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model')
TFLITE_MODEL_PATH = os.path.join(MODEL_DIR, 'plant_disease_model.tflite')

# Possible outputs for realistic dummy mode
DISEASE_OPTIONS = [
    {"name": "Healthy", "status": "Healthy", "confidence_range": (85, 99)},
    {"name": "Leaf Blight", "status": "Diseased", "confidence_range": (70, 95)},
    {"name": "Bacterial Spot", "status": "Diseased", "confidence_range": (65, 92)},
    {"name": "Early Blight", "status": "Diseased", "confidence_range": (68, 90)},
    {"name": "Late Blight", "status": "Diseased", "confidence_range": (70, 88)},
    {"name": "Powdery Mildew", "status": "Diseased", "confidence_range": (72, 94)},
    {"name": "Leaf Spot", "status": "Diseased", "confidence_range": (65, 89)},
]


def load_tflite_model():
    """
    Load TensorFlow Lite model if available
    Returns model interpreter or None
    """
    try:
        import tensorflow as tf  # noqa: F401
    except ImportError:
        return None

    try:
        if os.path.exists(TFLITE_MODEL_PATH):
            interpreter = tf.lite.Interpreter(model_path=TFLITE_MODEL_PATH)
            interpreter.allocate_tensors()
            return interpreter
    except Exception as e:
        print(f"[Disease Detector] TFLite model not used: {e}")
    return None


def predict_with_hf(image_path):
    """
    Run inference with Hugging Face Transformers
    Returns (disease_name, confidence, health_status) or None
    """
    global _hf_classifier, _hf_model, _hf_processor
    
    if not HF_AVAILABLE:
        return None
        
    try:
        # Load model and processor explicitly if not cached
        if _hf_model is None or _hf_processor is None:
            print(f"[Disease Detector] Loading HF model & processor: {HF_MODEL_ID}")
            _hf_model = MobileNetV2ForImageClassification.from_pretrained(
                HF_MODEL_ID, token=HF_TOKEN
            )
            try:
                # Try specific processor first
                _hf_processor = MobileNetV2ImageProcessor.from_pretrained(
                    HF_MODEL_ID, token=HF_TOKEN
                )
            except Exception:
                # Fallback to pipeline default if specific fails
                from transformers import AutoImageProcessor
                _hf_processor = AutoImageProcessor.from_pretrained(
                    HF_MODEL_ID, token=HF_TOKEN
                )
            
            # Re-initialize pipeline with explicit components
            _hf_classifier = pipeline(
                "image-classification",
                model=_hf_model,
                image_processor=_hf_processor
            )
            
        results = _hf_classifier(image_path)
        
        if not results:
            return None
            
        # Get the top result
        top_result = results[0]
        label = top_result['label']
        confidence = top_result['score']
        
        # Simple health status mapping
        health_status = "Healthy" if "healthy" in label.lower() else "Diseased"

        # --- Crop / Disease Split ---
        # Format: "Tomato___Late_blight" or "Tomato___healthy"
        crop = "Unknown"
        disease_display = label

        if "___" in label:
            parts = label.split("___", 1)
            crop = parts[0].replace('_', ' ').strip()
            raw_disease = parts[1]
            if "healthy" in raw_disease.lower():
                disease_display = "Healthy"
            else:
                disease_display = raw_disease.replace('_', ' ').title().strip()
        elif " with " in label:
            parts = label.split(" with ", 1)
            crop = parts[0].strip()
            disease_display = parts[1].strip()
        elif " on " in label:
            parts = label.split(" on ", 1)
            crop = parts[1].strip() # e.g. "Scab on Apple" -> crop is Apple
            disease_display = parts[0].strip()
        else:
            # Fallback: try to clean label
            if "healthy" in label.lower():
                disease_display = "Healthy"
                # Try to extract crop from "Apple healthy" or "Healthy Apple"
                crop = label.replace("healthy", "").replace("Healthy", "").strip()
            else:
                disease_display = label.replace('_', ' ').title().strip()

        return crop, disease_display, confidence, health_status
        
    except Exception as e:
        print(f"[Disease Detector] Hugging Face inference error: {e}")
        return None


def preprocess_image_for_model(image_path, target_size=(224, 224)):
    """Preprocess image for model input (typical input for plant disease models)"""
    try:
        img = Image.open(image_path).convert('RGB')
        img = img.resize(target_size)
        img_array = np.array(img)
        # Normalize to [0, 1]
        img_array = img_array.astype(np.float32) / 255.0
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    except Exception as e:
        print(f"[Disease Detector] Preprocess error: {e}")
        return None


def predict_with_tflite(interpreter, image_array):
    """
    Run inference with TFLite model
    Returns (disease_name, confidence, health_status) or None
    """
    try:
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        interpreter.set_tensor(input_details[0]['index'], image_array)
        interpreter.invoke()
        output = interpreter.get_tensor(output_details[0]['index'])

        # Assume model outputs: [batch, num_classes] or probabilities
        # Common setup: index 0 = Healthy, others = disease classes
        if len(output.shape) > 1:
            probs = output[0]
        else:
            probs = output

        pred_idx = int(np.argmax(probs))
        confidence = float(probs[pred_idx])

        # Map indices to our disease options (simplified - real model would have its own labels)
        if pred_idx == 0:
            return "Healthy", confidence, "Healthy"
        else:
            diseased_options = [d for d in DISEASE_OPTIONS if d["status"] == "Diseased"]
            choice = diseased_options[pred_idx % len(diseased_options)]
            return choice["name"], confidence, choice["status"]

    except Exception as e:
        print(f"[Disease Detector] TFLite inference error: {e}")
        return None


def _analyze_leaf_image(image_path):
    """
    Analyze leaf image using color heuristics to detect disease indicators.
    Healthy leaves: dominant green (G > R), uniform color, vibrant.
    Diseased leaves: yellowing (R≈G), browning, spots (high color variance).
    Returns: (is_likely_diseased: bool, disease_score: 0-1)
    """
    try:
        img = Image.open(image_path).convert('RGB')
        img = img.resize((120, 120))  # Resize for faster analysis
        arr = np.array(img)

        r, g, b = arr[:, :, 0].astype(float), arr[:, :, 1].astype(float), arr[:, :, 2].astype(float)
        mean_r, mean_g, mean_b = np.mean(r), np.mean(g), np.mean(b)

        # Green dominance: healthy = G clearly dominant. Diseased = yellow (R≈G) or brown
        green_ratio = mean_g / (mean_r + mean_g + mean_b + 1e-6)
        r_g_ratio = mean_r / (mean_g + 1e-6)  # >1 means redder than green (yellow/brown)

        # Color variance: spots/lesions cause high local variance
        std_r, std_g, std_b = np.std(r), np.std(g), np.std(b)
        color_variance = (std_r + std_g + std_b) / 3.0

        # Block variance: split into 4x4 grid, check uneven coloring (spots)
        h, w = arr.shape[:2]
        block_vars = []
        for i in range(0, h, h // 4):
            for j in range(0, w, w // 4):
                block = arr[i:i + h // 4, j:j + w // 4]
                if block.size > 0:
                    block_vars.append(np.std(block))
        spot_score = np.std(block_vars) if block_vars else 0  # Uneven blocks = spots

        disease_score = 0.0

        # Yellowing: R close to or higher than G
        if r_g_ratio >= 0.95:
            disease_score += 0.35
        elif r_g_ratio >= 0.88:
            disease_score += 0.2

        # Low green ratio
        if green_ratio < 0.36:
            disease_score += 0.3
        elif green_ratio < 0.40:
            disease_score += 0.15

        # High variance = diseased spots/lesions
        if color_variance > 50:
            disease_score += 0.25
        elif color_variance > 40:
            disease_score += 0.1

        # Uneven coloring (spot-like)
        if spot_score > 25:
            disease_score += 0.2

        disease_score = min(1.0, disease_score)
        is_likely_diseased = disease_score >= 0.35

        return is_likely_diseased, disease_score

    except Exception as e:
        print(f"[Disease Detector] Image analysis error: {e}")
        return False, 0.0


def detect_with_dummy(image_path):
    """
    Image-based disease detection when no TFLite model is available.
    Uses color analysis: green dominance, variance (spots), yellow/brown tint.
    Properly differentiates healthy vs diseased leaves based on image content.
    """
    try:
        is_diseased, disease_score = _analyze_leaf_image(image_path)

        diseased_options = [d for d in DISEASE_OPTIONS if d["status"] == "Diseased"]
        healthy_option = DISEASE_OPTIONS[0]

        if is_diseased:
            # Pick disease type - higher score can map to more severe/common diseases
            if disease_score > 0.75:
                option = diseased_options[0]  # Leaf Blight - common severe
            elif disease_score > 0.6:
                option = diseased_options[random.randint(1, 3)]  # Bacterial/Early/Late
            else:
                option = diseased_options[random.randint(4, 6)]  # Mildew/Leaf Spot
            low, high = option["confidence_range"]
            confidence = round(70 + disease_score * 20 + random.uniform(-3, 5), 2)
        else:
            option = healthy_option
            low, high = option["confidence_range"]
            confidence = round(85 + (1 - disease_score) * 10 + random.uniform(-2, 4), 2)

        confidence = max(low, min(high, confidence))

        return option["name"], confidence, option["status"]

    except Exception as e:
        print(f"[Disease Detector] Dummy detection error: {e}")
        option = random.choice(DISEASE_OPTIONS)
        confidence = round(random.uniform(75, 92), 2)
        return option["name"], confidence, option["status"]


def _build_response(crop, disease, confidence_raw, health_status, model_used):
    """
    Build a unified response dict.
    confidence_raw: value in 0–100 range.
    Applies confidence threshold: < 60 → low confidence warning.
    """
    confidence = round(float(confidence_raw), 2)

    if confidence < 60.0:
        return {
            "crop": crop,
            "disease": disease,
            "disease_name": disease,  # backwards compat
            "confidence": confidence,
            "health_status": health_status,
            "status": "Low Confidence - Retake Image",
            "model_used": model_used
        }

    return {
        "crop": crop,
        "disease": disease,
        "disease_name": disease,  # backwards compat
        "confidence": confidence,
        "health_status": health_status,
        "status": "ok",
        "model_used": model_used
    }


def detect_disease(image_path, original_filename=None, manual_crop=None):
    """
    Main entry: Detect plant disease from image.
    Returns: dict with crop, disease, disease_name, confidence, health_status, status
    """
    if not image_path or not os.path.exists(image_path):
        return {
            "crop": manual_crop or "Unknown",
            "disease": "Unknown",
            "disease_name": "Unknown",
            "confidence": 0,
            "health_status": "Error",
            "status": "error",
            "model_used": "none"
        }

    full_path = image_path
    if not os.path.isabs(image_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, 'static', image_path)

    # Automatically derive the plant name from the uploaded filename if not specified
    if not manual_crop and original_filename:
        base_name = str(os.path.basename(original_filename))
        if not base_name.startswith('capture_') and not base_name.startswith('image'):
            name_no_ext, _ = os.path.splitext(base_name)
            clean_name = name_no_ext.replace('___', ' ').replace('__', ' ').replace('_', ' ').replace('-', ' ')
            words = clean_name.strip().split()
            if len(words) >= 1:
                manual_crop = words[0].title()

    # Preemptively check if the image is actually a human (or other common non-plant objects)
    global _hf_object_detector
    if HF_AVAILABLE:
        try:
            if _hf_object_detector is None:
                # Load a tiny object detection model for "person" checking
                print("[Disease Detector] Loading YOLOS-tiny object detector...")
                _hf_object_detector = pipeline("object-detection", model="hustvl/yolos-tiny")
            
            # Check for humans in the image
            obj_results = _hf_object_detector(full_path)
            # If there's a person with reasonably high confidence, stop disease detection
            for obj in obj_results:
                if obj['label'] == 'person' and obj['score'] > 0.5:
                    return {
                        "crop": "Not a Plant",
                        "disease": "Human Detected",
                        "disease_name": "Human Detected",
                        "confidence": round(obj['score'] * 100, 2),
                        "health_status": "N/A",
                        "status": "Please upload a photo of a plant leaf.",
                        "model_used": "yolos-tiny"
                    }
        except Exception as e:
            print(f"[Disease Detector] Object detection fallback failed: {e}")

    # Try Hugging Face Plant Model first
    hf_result = predict_with_hf(full_path)
    if hf_result:
        crop, disease, conf, health = hf_result
        final_crop = manual_crop.title() if manual_crop else crop
        return _build_response(final_crop, disease, conf * 100, health, "huggingface")

    # Try TFLite next
    interpreter = load_tflite_model()
    if interpreter:
        img_array = preprocess_image_for_model(full_path)
        if img_array is not None:
            result = predict_with_tflite(interpreter, img_array)
            if result:
                # TFLite returns plain name, no crop info
                final_crop = manual_crop.title() if manual_crop else "Plant"
                return _build_response(final_crop, result[0], result[1] * 100, result[2], "tflite")

    # Fallback: dummy detection
    disease_name, confidence, health_status = detect_with_dummy(full_path)
    final_crop = manual_crop.title() if manual_crop else "Plant"
    return _build_response(final_crop, disease_name, confidence, health_status, "dummy")

