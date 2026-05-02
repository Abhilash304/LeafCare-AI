from disease_detector import predict_with_hf
import os

uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
images = [f for f in os.listdir(uploads_dir) if f.endswith('.jpg')]
if images:
    test_image = os.path.join(uploads_dir, images[0])
    print(f"Testing HF on {test_image}")
    result = predict_with_hf(test_image)
    print("Result:", result)
else:
    print("No images found.")
