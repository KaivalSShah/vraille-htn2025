from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import cohere
import PIL
import requests
import base64
import platform
import subprocess
import websocket
import threading
import json
import struct
import pyaudio
from vapiwebsockettts import VapiWebSocketTTS
import speech_recognition as sr

# Load environment variables from .env file
load_dotenv()

# Initialize Vapi WebSocket TTS
vapi_tts = None
if os.getenv("VAPI_PRIVATE_API_KEY"):
    vapi_tts = VapiWebSocketTTS(os.getenv("VAPI_PRIVATE_API_KEY"))

def speak_with_vapi(text: str):
    print(f"Speaking: {text}")
    """Use Vapi WebSocket to convert text to speech."""
    if not vapi_tts:
        print("❌ Vapi WebSocket TTS not available.")
        return
    
    success = vapi_tts.speak(text)
    if not success:
        print("🔄 Falling back to alternative TTS...")


# Define function declarations for the two tools
describe_image_declaration = {
    "name": "describe_image",
    "description": "Describe the image and return a detailed description of it",
    "parameters": {
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "The path to the image file to describe"
            }
        },
        "required": ["image_path"],
    },
}

# Actual function implementations
def describe_image(image_path: str) -> dict[str, str]:
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
                    {"type": "text", "text": "Describe the image and return a detailed description of it"},
                    {
                        "type": "image_url",
                        "image_url": {"url": base64_image_url},
                    },
                ],
            }
        ],
        temperature=0.3,
    )

    return {"message": response.message.content[0].text}


def continuous_speech_to_text(device_index=None):
    """
    Continuous speech recognition with microphone selection
    """
    recognizer = sr.Recognizer()

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    tools = [types.Tool(function_declarations=[describe_image_declaration])]
    config = types.GenerateContentConfig(tools=tools)
    
    # Initialize microphone with specified device index
    if device_index is not None:
        microphone = sr.Microphone(device_index=device_index)
        print(f"Using microphone device {device_index}")
    else:
        microphone = sr.Microphone()
        print("Using default microphone")
    
    # Adjust for ambient noise
    print("Adjusting for ambient noise... Please wait.")
    try:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=2)
    except Exception as e:
        print(f"Error accessing microphone: {e}")
        print("Please check if the microphone is connected and not being used by another application.")
        return
    
    print("Continuous speech recognition started.")
    print("Speak naturally - your speech will be transcribed in real-time.")
    print("Press Ctrl+C to stop.\n")
    
    while True:
        try:
            with microphone as source:
                # Listen for audio with timeout
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
            
            try:
                # Convert speech to text
                text = recognizer.recognize_google(audio)

                if text.strip():  # Only print non-empty transcriptions
                    print(f">> {text}")
                    # pass text to gemini
                    contents = [
                        types.Content(role="user", parts=[types.Part(text=text)])
                    ]

                try:
                    # Send request with function declarations
                    response = client.models.generate_content(
                        model="gemini-2.0-flash-exp",
                        contents=contents,
                        config=config,
                    )
                    
                    # Check if the model wants to call a function
                    if response.candidates[0].content.parts[0].function_call:
                        function_call = response.candidates[0].content.parts[0].function_call
                        function_name = function_call.name
                        function_args = function_call.args or {}
                        
                        # Execute the function if it exists
                        if function_name in available_functions:
                            result = available_functions[function_name](**function_args)
                            print(f"Function result: {result['message']}")
                            
                            # Send the function result back to the model for a final response
                            function_result_content = types.Content(
                                role="function",
                                parts=[types.Part(
                                    function_response=types.FunctionResponse(
                                        name=function_name,
                                        response=result
                                    )
                                )]
                            )
                            
                            # Add the function result to the conversation and get final response
                            contents.append(function_result_content)
                            final_response = client.models.generate_content(
                                model="gemini-2.0-flash-exp",
                                contents=contents,
                                config=config,
                            )
                            
                            print(f"Assistant: {final_response.candidates[0].content.parts[0].text}")
                            speak_with_vapi(final_response.candidates[0].content.parts[0].text)
                        else:
                            print(f"Function {function_name} not found!")
                    else:
                        # Direct text response from the model
                        print(f"Assistant: {response.candidates[0].content.parts[0].text}")
                        speak_with_vapi(response.candidates[0].content.parts[0].text)
                        
                except Exception as e:
                    print(f"Error: {e}")
                    
            except sr.UnknownValueError:
                # Ignore unclear audio - don't print anything
                pass
                
        except sr.WaitTimeoutError:
            # No speech detected - continue listening
            pass
        except KeyboardInterrupt:
            print("\n\nStopping speech recognition...")
            print("Goodbye!")
            break
        except sr.RequestError as e:
            print(f"Error with speech recognition service: {e}")
            print("Please check your internet connection and try again.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

# Function mapping for execution
available_functions = {
    "describe_image": describe_image,
}

def main():

    print("microphone speech to text setup")
    print("=" * 40)
    device_index = 1
    continuous_speech_to_text(device_index)
    # Configure the client and tools
    # client = genai.Client(
    #     api_key=os.getenv("GEMINI_API_KEY"),
    # )
    # tools = types.Tool(function_declarations=[hello_world_5_declaration, hello_world_10_declaration, describe_image_declaration])
    # config = types.GenerateContentConfig(tools=[tools])
    
    # print("Hello World Function Calling Demo with Vapi WebSocket TTS")
    # print("Available commands:")
    # print(", ".join(available_functions.keys()))
    # print("- Type 'quit' to exit")
    # print("- Results will be read aloud using Vapi WebSocket TTS\n")
    
    # while True:
    #     user_input = input("User: ")
        
    #     if user_input.lower() in ['quit', 'exit', 'q']:
    #         print("Goodbye!")
    #         break
            
    #     # Create content for the model
    #     contents = [
    #         types.Content(
    #             role="user", 
    #             parts=[types.Part(text=user_input)]
    #         )
    #     ]
        
    #     try:
    #         # Send request with function declarations
    #         response = client.models.generate_content(
    #             model="gemini-2.0-flash-exp",
    #             contents=contents,
    #             config=config,
    #         )
            
    #         # Check if the model wants to call a function
    #         if response.candidates[0].content.parts[0].function_call:
    #             function_call = response.candidates[0].content.parts[0].function_call
    #             function_name = function_call.name
    #             function_args = function_call.args or {}
                
    #             # Execute the function if it exists
    #             if function_name in available_functions:
    #                 result = available_functions[function_name](**function_args)
    #                 print(f"Function result: {result['message']}")
                    
    #                 # Send the function result back to the model for a final response
    #                 function_result_content = types.Content(
    #                     role="function",
    #                     parts=[types.Part(
    #                         function_response=types.FunctionResponse(
    #                             name=function_name,
    #                             response=result
    #                         )
    #                     )]
    #                 )
                    
    #                 # Add the function result to the conversation and get final response
    #                 contents.append(function_result_content)
    #                 final_response = client.models.generate_content(
    #                     model="gemini-2.0-flash-exp",
    #                     contents=contents,
    #                     config=config,
    #                 )
                    
    #                 print(f"Assistant: {final_response.candidates[0].content.parts[0].text}")
    #                 speak_with_vapi(final_response.candidates[0].content.parts[0].text)
    #             else:
    #                 print(f"Function {function_name} not found!")
    #         else:
    #             # Direct text response from the model
    #             print(f"Assistant: {response.candidates[0].content.parts[0].text}")
                
    #     except Exception as e:
    #         print(f"Error: {e}")
        
    #     print()  # Add blank line for readability

if __name__ == "__main__":
    main()