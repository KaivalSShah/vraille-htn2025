import cohere
import base64
import os

from dotenv import load_dotenv

load_dotenv()

def generate_text(image_path, message):

    model = "c4ai-aya-vision-8b"

    co = cohere.ClientV2(os.getenv("COHERE_API_KEY"))

    with open(image_path, "rb") as img_file:
        base64_image_url = f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode('utf-8')}"

    response = co.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": message},
                    {
                        "type": "image_url",
                        "image_url": {"url": base64_image_url},
                    },
                ],
            }
        ],
        temperature=0.3,
    )

    print(response.message.content[0].text)

generate_text("image.png", "What is the image?")