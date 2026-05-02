"""
app.py - Main Flask application for AI-Powered Smart Farming Hub
Routes: Dashboard, Disease Detection, API endpoints for sensors and capture
"""

import os
import json
import base64
from datetime import datetime
from flask import Flask, render_template, jsonify, request

# Import our modules
import database
from sensors_simulator import sensor_simulator
from camera_capture import capture_image, is_camera_available
from disease_detector import detect_disease
from recommendation_engine import get_recommendation

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smart-farming-hub-2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max


# Initialize database on startup
with app.app_context():
    database.init_db()


# ============== ROUTES ==============

@app.route('/')
def dashboard():
    """Dashboard - Home page with sensor overview"""
    return render_template('dashboard.html')


@app.route('/disease')
def disease_page():
    """Disease detection page - camera capture and analysis"""
    camera_ok = is_camera_available()
    return render_template('disease.html', camera_available=camera_ok)


@app.route('/history')
def history_page():
    """History page - view previous detections"""
    detections = database.get_disease_history(limit=50)
    
    # Parse recommendations from JSON for each detection
    for det in detections:
        if det['recommendation']:
            try:
                det['recommendation_data'] = json.loads(det['recommendation'])
            except json.JSONDecodeError:
                det['recommendation_data'] = None
        else:
            det['recommendation_data'] = None
            
    return render_template('history.html', history=detections)


@app.route('/api/sensor-data')
def api_sensor_data():
    """
    API: Get current sensor values (simulated)
    Called every 5 seconds by dashboard AJAX
    """
    try:
        data = sensor_simulator.read_all()

        # Safe extraction with defaults so the API never crashes on missing keys
        temp = data.get('temperature', 0.0)
        humidity = data.get('humidity', 0.0)
        soil_moisture = data.get('soil_moisture', 0.0)

        # Determine status colors for UI
        # Temperature: 25-30 good, 30-35 warning, >35 critical
        if temp <= 30:
            data['temp_status'] = 'good'
        elif temp <= 35:
            data['temp_status'] = 'warning'
        else:
            data['temp_status'] = 'critical'

        # Humidity: 50-70 good, 40-50 or 70-80 warning, <40 or >80 critical
        if 50 <= humidity <= 70:
            data['humidity_status'] = 'good'
        elif 40 <= humidity <= 80:
            data['humidity_status'] = 'warning'
        else:
            data['humidity_status'] = 'critical'

        return jsonify({
            'temperature': temp,
            'humidity': humidity,
            'soil_moisture': soil_moisture,
            'temp_status': data.get('temp_status', 'good'),
            'humidity_status': data.get('humidity_status', 'good'),
            'irrigation_prediction': data.get('irrigation_prediction', False),
            'irrigation_confidence': data.get('irrigation_confidence', 0.0),
            'irrigation_status': data.get('irrigation_status', 'OFF'),
            'manual_mode': data.get('manual_mode', False),
            'data_source': data.get('data_source', 'Unknown'),
            'timestamp': data.get('timestamp', '')
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'temperature': 0.0,
            'humidity': 0.0,
            'soil_moisture': 0.0,
            'temp_status': 'good',
            'humidity_status': 'good',
            'irrigation_status': 'OFF',
            'irrigation_prediction': False,
            'irrigation_confidence': 0.0,
            'manual_mode': False,
            'data_source': 'Error',
            'timestamp': ''
        }), 200  # Return 200 with defaults so frontend doesn't break


@app.route('/api/capture-and-detect', methods=['POST'])
def api_capture_and_detect():
    """
    API: Accept base64 image from browser webcam OR capture from OpenCV camera.
    Returns: crop, disease, confidence, health_status, status, recommendation
    """
    try:
        uploads_dir = os.path.join(app.static_folder, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)

        # --- Path A: Browser sends base64 image ---
        body = request.get_json(silent=True)
        manual_crop = None
        if body:
            manual_crop = body.get('plant_name')
            if body.get('image'):
                img_data = body['image']
                # Strip data URL prefix if present
                if ',' in img_data:
                    img_data = img_data.split(',', 1)[1]
                filename = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                filepath = os.path.join(uploads_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(base64.b64decode(img_data))
                image_path = f'uploads/{filename}'
                full_image_path = filepath

        # --- Path B: Fallback - use OpenCV / camera_capture.py ---
        if not body or not body.get('image'):
            success, result = capture_image()
            if not success:
                return jsonify({'success': False, 'error': result}), 200
            image_path = result
            full_image_path = os.path.join(app.static_folder, image_path)
            if not os.path.exists(full_image_path):
                full_image_path = os.path.join(os.path.dirname(__file__), 'static', image_path)

        # Step 2: Run disease detection
        detection = detect_disease(full_image_path, manual_crop=manual_crop)

        disease_name = detection.get('disease_name', detection.get('disease', 'Unknown'))
        crop        = detection.get('crop', 'Plant')
        disease     = detection.get('disease', disease_name)
        confidence  = detection.get('confidence', 0)
        health_status = detection.get('health_status', 'Unknown')
        det_status  = detection.get('status', 'ok')

        # Step 3: Get recommendation
        rec = get_recommendation(disease_name, health_status)
        rec_text = json.dumps(rec)

        # Step 4: Store in database
        database.insert_disease_detection(
            image_path=image_path,
            disease_name=disease_name,
            confidence=confidence,
            health_status=health_status,
            recommendation=rec_text
        )

        return jsonify({
            'success': True,
            'image_path': f'/static/{image_path}',
            'crop': crop,
            'disease': disease,
            'disease_name': disease_name,
            'confidence': confidence,
            'health_status': health_status,
            'status': det_status,
            'recommendation': rec
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'image_path': None,
            'crop': None,
            'disease': None,
            'disease_name': None,
            'confidence': None,
            'health_status': None,
            'status': 'error',
            'recommendation': None
        }), 500


@app.route('/api/upload-and-detect', methods=['POST'])
def api_upload_and_detect():
    """
    API: Accept file upload from browser.
    Returns: crop, disease, confidence, health_status, status, recommendation
    """
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'}), 400
            
        uploads_dir = os.path.join(app.static_folder, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        filename = file.filename
        filepath = os.path.join(uploads_dir, filename)
        file.save(filepath)
        
        image_path = f'uploads/{filename}'
        full_image_path = filepath
        
        # Step 2: Run disease detection with original filename
        detection = detect_disease(full_image_path, original_filename=filename)
        
        disease_name = detection.get('disease_name', detection.get('disease', 'Unknown'))
        crop        = detection.get('crop', 'Plant')
        disease     = detection.get('disease', disease_name)
        confidence  = detection.get('confidence', 0)
        health_status = detection.get('health_status', 'Unknown')
        det_status  = detection.get('status', 'ok')

        # Step 3: Get recommendation
        rec = get_recommendation(disease_name, health_status)
        rec_text = json.dumps(rec)

        # Step 4: Store in database
        database.insert_disease_detection(
            image_path=image_path,
            disease_name=disease_name,
            confidence=confidence,
            health_status=health_status,
            recommendation=rec_text
        )

        return jsonify({
            'success': True,
            'image_path': f'/static/{image_path}',
            'crop': crop,
            'disease': disease,
            'disease_name': disease_name,
            'confidence': confidence,
            'health_status': health_status,
            'status': det_status,
            'recommendation': rec
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/camera-status')
def api_camera_status():
    """Check if camera is available"""
    return jsonify({'available': is_camera_available()})

@app.route('/api/irrigation/toggle', methods=['POST'])
def api_irrigation_toggle():
    """
    API: Toggle irrigation manual override
    Expects JSON: { "mode": "auto"|"manual", "status": "ON"|"OFF" }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        mode = data.get('mode', 'auto')
        status = data.get('status', 'OFF')
        
        sensor_simulator.set_manual_override(mode, status)
        
        return jsonify({
            'success': True, 
            'message': f"Irrigation set to {mode.upper()}" + (f" ({status})" if mode == 'manual' else "")
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



# ============== RUN ==============

if __name__ == '__main__':
    # Create static uploads dir if not exists
    uploads_path = os.path.join(app.static_folder, 'uploads')
    if not os.path.exists(uploads_path):
        os.makedirs(uploads_path)

    print("\n" + "="*50)
    print("  AI-Powered Smart Farming Hub")
    print("  Dashboard: http://127.0.0.1:5000/")
    print("  Disease Detection: http://127.0.0.1:5000/disease")
    print("="*50 + "\n")

    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
