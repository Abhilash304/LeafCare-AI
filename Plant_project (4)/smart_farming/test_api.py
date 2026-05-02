import requests
import json
import base64
import os

def test_manual_crop():
    url = "http://127.0.0.1:5000/api/capture-and-detect"
    
    # create a dummy image to test with
    test_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads', 'capture_20260205_050854.jpg')
    if not os.path.exists(test_image_path):
        uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
        images = [f for f in os.listdir(uploads_dir) if f.endswith('.jpg')]
        if images:
            test_image_path = os.path.join(uploads_dir, images[0])
        else:
            print("No image found.")
            return

    with open(test_image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    payload = {
        "image": f"data:image/jpeg;base64,{encoded_string}",
        "plant_name": "Orange"
    }

    print("Sending request with manual crop 'Orange'...")
    response = requests.post(url, json=payload)
    print("Status Code:", response.status_code)
    try:
        data = response.json()
        print("CROP:", data.get('crop'))
        print("DISEASE:", data.get('disease_name'))
        print("SUCCESS:", data.get('success'))
    except Exception as e:
        print("Error parsing JSON:", response.text)

if __name__ == "__main__":
    test_manual_crop()
