import os
import cohere
import base64
from dotenv import load_dotenv
import cv2
import base64
import requests

# Load environment variables
load_dotenv()

def read_text() -> dict[str, str]:
    model = "c4ai-aya-vision-8b"
    co = cohere.ClientV2(os.getenv("COHERE_API_KEY"))

    # open camera
    cap = cv2.VideoCapture(1) # 0 built-in webcam, 1 is virtual cam
    if not cap.isOpened():
        return {"message": "❌ Could not access the camera."}

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return {"message": "❌ Failed to capture image from camera."}

    # Encode captured frame as JPEG
    _, buffer = cv2.imencode(".jpg", frame)
    base64_image_url = f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"

    # Send to Cohere vision model - Fixed the image_url structure
    response = co.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Read/transcribe the text to the fullest of your ability from the image and return as much of it you were able to transcribe"},
                    {"type": "image_url", "image_url": {"url": base64_image_url}},  # Fixed: wrapped in object with 'url' key
                ],
            }
        ],
        temperature=0.3,
    )

    return {"message": response.message.content[0].text}

def describe_image() -> dict[str, str]:
    model = "c4ai-aya-vision-8b"
    co = cohere.ClientV2(os.getenv("COHERE_API_KEY"))

    # open camera
    cap = cv2.VideoCapture(1) # 0 built-in webcam, 1 is virtual cam
    if not cap.isOpened():
        return {"message": "❌ Could not access the camera."}

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return {"message": "❌ Failed to capture image from camera."}

    # Encode captured frame as JPEG
    _, buffer = cv2.imencode(".jpg", frame)
    base64_image_url = f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"

    # Send to Cohere vision model - Fixed the image_url structure
    response = co.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe the image and return a detailed description of it"},
                    {"type": "image_url", "image_url": {"url": base64_image_url}},  # Fixed: wrapped in object with 'url' key
                ],
            }
        ],
        temperature=0.3,
    )

    return {"message": response.message.content[0].text}

# recognize face
def recognize_face() -> dict[str, str]:
    # Open camera
    cap = cv2.VideoCapture(1)  # 0 for default webcam, 1 for external
    if not cap.isOpened():
        return {"message": "❌ Could not access the camera."}

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return {"message": "❌ Failed to capture image from camera."}

    # Encode captured frame as JPEG
    _, buffer = cv2.imencode(".jpg", frame)
    image_base64 = base64.b64encode(buffer).decode("utf-8")

    # Send to Face++ search API
    url = "https://api-us.faceplusplus.com/facepp/v3/search"
    payload = {
        "api_key": os.getenv("FACEPP_API_KEY"),
        "api_secret": os.getenv("FACEPP_API_SECRET"),
        "outer_id": os.getenv("FACEPP_OUTER_ID"),
        "image_base64": image_base64,
    }

    try:
        response = requests.post(url, data=payload)
        result = response.json()

        if "error_message" in result:
            return {"message": f"❌ Face++ error: {result['error_message']}"}

        if "results" not in result or len(result["results"]) == 0:
            return {"message": "⚠️ No matching face found."}

        top_match = result["results"][0]
        face_token = top_match["face_token"]
        confidence = top_match["confidence"]

        # fetch the name from the supabase database table called facedb structured as [face_id] -> [name]
        supabase_url = os.getenv('SUPABASE_URL')  # This already contains https://
        url = f"{supabase_url}/rest/v1/facedb?face_id=eq.{face_token}"
        headers = {
            "apikey": os.getenv("SUPABASE_API_KEY"),
            "Authorization": f"Bearer {os.getenv('SUPABASE_API_KEY')}",
            "Content-Type": "application/json"
        }

        print(f"🔍 Querying Supabase: {url}")
        response = requests.get(url, headers=headers)
        print(f"📡 Response status: {response.status_code}")
        print(f"📄 Response body: {response.text}")

        if response.status_code != 200:
            return {"message": f"❌ Supabase query failed with status {response.status_code}: {response.text}"}

        data = response.json()
        if not data or len(data) == 0:
            return {"message": f"❌ No person found with face token: {face_token}"}

        name = data[0]["name"]

        return {
            "name": name,
            "confidence": confidence,
            "message": f"Detected {name} with {confidence:.2f} confidence"
        }

    except Exception as e:
        return {"message": f"❌ Exception occurred: {e}"}

# Function mapping for execution
AVAILABLE_FUNCTIONS = {
    "describe_image": describe_image,
    "recognize_face": recognize_face,
    # Add new functions to this mapping as you create them
}
