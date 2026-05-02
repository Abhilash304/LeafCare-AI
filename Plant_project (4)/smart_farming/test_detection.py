
import os
import sys
from disease_detector import detect_disease

# Add the current directory to path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_on_uploads():
    uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    if not os.path.exists(uploads_dir):
        print(f"Directory not found: {uploads_dir}")
        return

    # List some files to test
    files = [f for f in os.listdir(uploads_dir) if f.endswith('.jpg')]
    if not files:
        print("No JPG files found in uploads.")
        return

    # Test on up to 5 files
    test_files = files[:5]
    
    print(f"Testing detection on {len(test_files)} images...\n")
    print(f"{'File':<35} | {'Crop':<15} | {'Disease':<25} | {'Conf':<6} | {'Status'}")
    print("-" * 100)
    
    for filename in test_files:
        filepath = os.path.join(uploads_dir, filename)
        try:
            result = detect_disease(filepath, original_filename=filename)
            print(f"FILE: {filename}")
            print(f"  CROP: {result.get('crop', 'Unknown')}")
            print(f"  DISEASE: {result.get('disease', 'Unknown')}")
            print(f"  CONFIDENCE: {result.get('confidence', 0):.1f}")
            print(f"  STATUS: {result.get('status', 'ok')}")
            print("-" * 20)
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    test_on_uploads()
