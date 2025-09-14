import os
import cohere
import base64
from dotenv import load_dotenv
import cv2
import base64

# Load environment variables
load_dotenv()

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

    # Show captured frame in a window
    # cv2.imshow("Captured Image", frame)
    # print("📷 Press any key in the image window to continue...")
    # cv2.waitKey(0)  # wait for a key press
    # cv2.destroyAllWindows()

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

# Add more tool function implementations here
# Example for future tools:

# def read_text_from_camera() -> dict[str, str]:
#     """Use camera to read text from the current view."""
#     # Implementation here
#     return {"message": "Text reading functionality not implemented yet"}

# def identify_objects() -> dict[str, str]:
#     """Identify objects in the camera view."""
#     # Implementation here  
#     return {"message": "Object identification functionality not implemented yet"}

# def get_current_location() -> dict[str, str]:
#     """Get the user's current GPS coordinates and address."""
#     # Implementation here
#     return {"message": "Location functionality not implemented yet"}

# Function mapping for execution
AVAILABLE_FUNCTIONS = {
    "describe_image": describe_image,
    # Add new functions to this mapping as you create them
}
