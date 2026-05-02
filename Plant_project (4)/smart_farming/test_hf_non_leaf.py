from disease_detector import predict_with_hf
import os

def test_existing_model():
    print("Testing existing HF plant model on a known human/non-sheet image...")
    # Let's see how the model behaves on something that isn't a leaf.
    # We will upload a dummy human image or check an existing one.
    upload_dir = 'static/uploads'
    
    # Check what images we have
    if os.path.exists(upload_dir):
        files = [f for f in os.listdir(upload_dir) if f.endswith('.jpg') or f.endswith('.png')]
        
        # Test on the latest uploaded image (which the user might have just taken of a human)
        if files:
            img_path = os.path.join(upload_dir, files[-1])
            print(f"Testing HF model on {img_path}")
            result = predict_with_hf(img_path)
            print("Result:", result)
        else:
            print("No images found.")
            
if __name__ == "__main__":
    test_existing_model()
