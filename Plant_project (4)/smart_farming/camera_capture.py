"""
camera_capture.py - Captures images using laptop built-in camera via OpenCV
Uses VideoCapture(0) - handles camera errors gracefully
"""

import cv2
import os
from datetime import datetime


# Path to store captured images
UPLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')


def ensure_uploads_dir():
    """Create uploads directory if it doesn't exist"""
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)


def capture_image():
    """
    Capture a single frame from laptop camera (index 0)
    Returns: (success: bool, image_path: str or error_message: str)
    """
    ensure_uploads_dir()

    # Try to open laptop camera - index 0 is typically built-in webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return False, "Camera not available. Please check if your laptop camera is connected and not in use by another application."

    try:
        # Read a few frames to allow camera to warm up (helps with auto-focus)
        for _ in range(3):
            ret, frame = cap.read()
            if not ret:
                break

        if not ret or frame is None:
            return False, "Failed to capture image from camera."

        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"capture_{timestamp}.jpg"
        filepath = os.path.join(UPLOADS_DIR, filename)
        relative_path = f"uploads/{filename}"

        # Save the captured frame
        success = cv2.imwrite(filepath, frame)

        cap.release()
        cv2.destroyAllWindows()

        if success:
            return True, relative_path
        else:
            return False, "Failed to save captured image."

    except Exception as e:
        if cap:
            cap.release()
        cv2.destroyAllWindows()
        return False, f"Camera error: {str(e)}"


def is_camera_available():
    """Check if camera is available without capturing"""
    cap = cv2.VideoCapture(0)
    available = cap.isOpened()
    cap.release()
    return available
