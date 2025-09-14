import requests
import json
import websocket
import threading
import pyaudio
import time

from dotenv import load_dotenv
load_dotenv()

class VapiWebSocketTTS:
    def __init__(self, api_key):
        self.api_key = api_key
        self.ws = None
        self.audio = None
        self.stream = None
        self.is_playing = False
        self.tts_complete = threading.Event()
        self.tts_started = threading.Event()
        
    def create_websocket_call(self, text):
        """Create a WebSocket call for TTS."""
        url = "https://api.vapi.ai/call"
        headers = {
            'authorization': f'Bearer {self.api_key}',
            'content-type': 'application/json'
        }
        
        # Create assistant for TTS
        payload = {
            "assistant": {
                "name": "TTS Assistant",
                "firstMessage": text,
                "context": "You are a text-to-speech assistant. Read the provided text exactly as given.",
                "model": {
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a text-to-speech assistant. Read the user's message aloud exactly as provided."
                        }
                    ]
                },
                "voice": {
                    "provider": "playht",
                    "voiceId": "jennifer"
                },
                "recordingEnabled": False,
                "interruptionsEnabled": False,
                "endCallMessage": "",
                "maxDurationSeconds": 60
            },
            "transport": {
                "provider": "vapi.websocket",
                "audioFormat": {
                    "format": "pcm_s16le",
                    "container": "raw",
                    "sampleRate": 16000
                }
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            return response.json()
        else:
            print(f"❌ Failed to create WebSocket call: {response.status_code} - {response.text}")
            return None
    
    def on_message(self, ws, message):
        """Handle WebSocket messages."""
        if isinstance(message, bytes):
            # This is audio data
            self.play_audio_chunk(message)
        else:
            # This is a control message
            try:
                data = json.loads(message)
                if data.get('type') == 'call.started':
                    print("✅ TTS call started")
                    self.tts_started.set()
                elif data.get('type') == 'call.ended':
                    print("✅ TTS call ended")
                    self.tts_complete.set()
                    self.cleanup()
            except json.JSONDecodeError:
                pass
    
    def on_error(self, ws, error):
        """Handle WebSocket errors."""
        print(f"❌ WebSocket error: {error}")
        self.tts_complete.set()  # Signal completion on error
    
    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close."""
        print("🔊 WebSocket connection closed")
        self.tts_complete.set()  # Signal completion when closed
        self.cleanup()
    
    def on_open(self, ws):
        """Handle WebSocket open."""
        print("🔊 WebSocket connection opened")
        # Initialize audio playback
        self.setup_audio()
    
    def setup_audio(self):
        """Set up audio playback."""
        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                output=True,
                frames_per_buffer=1024,
                output_device_index=2  # 5 is Input device (default speaker)
                # output_device_index=7  # 5 is Input device (default speaker)
            )
            self.is_playing = True
        except Exception as e:
            print(f"❌ Error setting up audio: {e}")
    
    def play_audio_chunk(self, audio_data):
        """Play audio chunk."""
        if self.stream and self.is_playing:
            try:
                self.stream.write(audio_data)
            except Exception as e:
                print(f"❌ Error playing audio: {e}")
    
    def cleanup(self):
        """Clean up audio resources."""
        self.is_playing = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
    
    def speak(self, text):
        """Convert text to speech using Vapi WebSocket."""
        print("🔊 Starting Vapi WebSocket TTS...")
        
        # Reset events for new TTS session
        self.tts_complete.clear()
        self.tts_started.clear()
        
        # Create WebSocket call
        call_data = self.create_websocket_call(text)
        if not call_data:
            return False
        
        # Get WebSocket URL
        ws_url = call_data.get('transport', {}).get('websocketCallUrl')
        if not ws_url:
            print("❌ No WebSocket URL in response")
            return False
        
        print(f"📞 Connecting to WebSocket: {ws_url}")
        
        # Create WebSocket connection
        websocket.enableTrace(False)  # Set to True for debugging
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        
        # Run WebSocket in a separate thread
        def run_websocket():
            self.ws.run_forever()
        
        ws_thread = threading.Thread(target=run_websocket)
        ws_thread.daemon = True
        ws_thread.start()
        
        # Wait for TTS to start (with timeout)
        if self.tts_started.wait(timeout=10):
            # Wait for TTS to complete (with timeout)
            if self.tts_complete.wait(timeout=60):
                print("🎵 TTS playback completed")
                return True
            else:
                print("⏰ TTS timeout - continuing anyway")
                return False
        else:
            print("⏰ TTS failed to start - timeout")
            return False
