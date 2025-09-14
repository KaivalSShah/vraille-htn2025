import requests
import time

ARDUINO_IP = "10.37.97.204"  # Update this with your Arduino's IP
PORT = 8080

def send_braille_pattern(pattern: str):
    """Send 6-bit pattern to Arduino via HTTP GET request."""
    try:
        url = f"http://{ARDUINO_IP}:{PORT}/braille/{pattern}"
        print(f"📤 Sending HTTP request to: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Success! Arduino response: {response.text.strip()}")
            return True
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Timeout: Arduino didn't respond within 5 seconds")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Can't reach Arduino at {ARDUINO_IP}:{PORT}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def english_to_braille(text: str) -> list:
    """Convert text to 6-bit Braille patterns."""
    braille_dict = {
        'a': '100000', 'b': '101000', 'c': '110000', 'd': '110100',
        'e': '100100', 'f': '111000', 'g': '111100', 'h': '101100',
        'i': '011000', 'j': '011100', 'k': '100010', 'l': '101010',
        'm': '110010', 'n': '110110', 'o': '100110', 'p': '111010',
        'q': '111110', 'r': '101110', 's': '011010', 't': '011110',
        'u': '100011', 'v': '101011', 'w': '011101', 'x': '110011',
        'y': '110111', 'z': '100111',
        '1': '100000', '2': '101000', '3': '110000', '4': '110100',
        '5': '100100', '6': '111000', '7': '111100', '8': '101100',
        '9': '011000', '0': '011100',
        '.': '010011', ',': '010000', '?': '011001', '!': '011010',
        '-': '001001', "'": '000010', ':': '010010', ';': '011000',
        ' ': '000000'
    }

    NUMBER_PREFIX = '001111'
    CAPITAL_INDICATOR = '000001'

    braille_output = []
    for char in text:
        if char.isupper():
            braille_output.append(CAPITAL_INDICATOR)
            char = char.lower()
        if char.isdigit():
            braille_output.append(NUMBER_PREFIX)
        braille_pattern = braille_dict.get(char, '000000')
        braille_output.append(braille_pattern)
    
    return braille_output

def display_braille_on_arduino(braille_patterns: list, delay_between_chars: float = 1.0):
    """Send each pattern to Arduino with delays."""
    print(f"🎯 Displaying {len(braille_patterns)} characters on Arduino...")
    print("=" * 50)
    
    for i, pattern in enumerate(braille_patterns):
        print(f"\n📍 Character {i+1}/{len(braille_patterns)}: {pattern}")
        
        success = send_braille_pattern(pattern)
        if not success:
            print(f"❌ Failed to send pattern {pattern}")
            continue
        
        if i < len(braille_patterns) - 1:
            print(f"⏳ Waiting {delay_between_chars} seconds before next character...")
            time.sleep(delay_between_chars)
    
    print("\n" + "=" * 50)
    print("🎉 Display sequence complete!")

def form_brailles(text: str, display_delay: float = 1.0) -> dict:
    """Convert text to Braille and display on Arduino."""
    try:
        print(f"🔤 Converting text to Braille: '{text}'")
        braille_patterns = english_to_braille(text)
        
        print(f"📋 Generated {len(braille_patterns)} Braille patterns:")
        for i, pattern in enumerate(braille_patterns):
            print(f"   {i+1}. {pattern}")
        
        display_braille_on_arduino(braille_patterns, display_delay)
        
        return {
            "message": f"Success: '{text}' displayed on Arduino",
            "original_text": text,
            "braille_patterns": braille_patterns,
            "character_count": len(braille_patterns)
        }
        
    except Exception as e:
        error_msg = f"Error: {e}"
        print(f"❌ {error_msg}")
        return {"message": error_msg}

def test_single_pattern(pattern: str):
    """Test single 6-bit pattern."""
    if len(pattern) != 6 or not all(bit in '01' for bit in pattern):
        print(f"❌ Invalid pattern: '{pattern}' (must be exactly 6 bits of 0s and 1s)")
        return False
    
    print(f"🧪 Testing single pattern: {pattern}")
    return send_braille_pattern(pattern)

def test_connection():
    """Test if Arduino is reachable."""
    print("🔍 Testing connection to Arduino...")
    return test_single_pattern("000000")

if __name__ == "__main__":
    print("🚀 Braille Display System - Python Controller")
    print("=" * 50)
    
    # Test connection first
    if not test_connection():
        print("❌ Cannot connect to Arduino. Check IP address and WiFi connection.")
        exit(1)
    
    print("\n✅ Connection test successful!")
    print("\n" + "=" * 50)
    
    # Test with "Hello"
    # result = form_brailles("Hello", display_delay=2.0)
    # print(f"\n📊 Final result: {result['message']}")
    
    print("\n" + "=" * 50)
    
    # Test individual patterns
    print("🧪 Testing individual patterns:")
    test_patterns = ["101100", "100100", "101010", "101010", "100110"]  # h, e, l, l, o
    # test_patterns = ["111111"]
    
    for pattern in test_patterns:
        test_single_pattern(pattern)
        time.sleep(2)
    
    print("\n🎉 All tests completed!")