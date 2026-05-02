import time
try:
    from transformers import pipeline
except ImportError:
    print("Transformers not installed.")
    exit()

def test_yolos():
    print("Loading YOLOS-tiny...")
    start = time.time()
    # YOLOS-tiny is extremely small and fast for COCO 80 classes (includes 'person')
    detector = pipeline("object-detection", model="hustvl/yolos-tiny")
    print(f"Loaded in {time.time() - start:.2f}s")
    
    # We need a sample image
    # Let's see if there is any image in static/uploads
    import os
    upload_dir = 'static/uploads'
    if os.path.exists(upload_dir):
        files = [f for f in os.listdir(upload_dir) if f.endswith('.jpg') or f.endswith('.png')]
        if files:
            img_path = os.path.join(upload_dir, files[-1]) # use latest
            print(f"Testing on {img_path}...")
            start = time.time()
            results = detector(img_path)
            print(f"Inference in {time.time() - start:.2f}s")
            print("Results:", results)
        else:
            print("No test images found.")
    else:
        print("Upload dir not found.")

if __name__ == "__main__":
    test_yolos()
