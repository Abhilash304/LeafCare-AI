import requests
import os

def test_upload():
    url = "http://127.0.0.1:5000/api/upload-and-detect"
    
    # create a dummy image to test with
    uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    images = [f for f in os.listdir(uploads_dir) if f.endswith('.jpg')]
    if not images:
        print("No image found.")
        return
        
    test_image_path = os.path.join(uploads_dir, images[0])
    
    # We will upload this file, but rename it in the request to test filename parsing
    files = {"file": ("Strawberry___healthy.jpg", open(test_image_path, "rb"), "image/jpeg")}
    
    print("Sending upload request with filename 'Strawberry___healthy.jpg'...")
    response = requests.post(url, files=files)
    print("Status Code:", response.status_code)
    try:
        data = response.json()
        print("CROP:", data.get('crop'))
        print("DISEASE:", data.get('disease_name'))
        print("SUCCESS:", data.get('success'))
    except Exception as e:
        print("Error parsing JSON:", response.text)

if __name__ == "__main__":
    test_upload()
