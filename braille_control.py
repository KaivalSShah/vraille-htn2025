import socket
import time

ARDUINO_IP = "10.37.114.81"  # Replace with Arduino's IP from Serial Monitor
PORT = 8080

def send_servo_angle(angle: int):
    """Send servo angle command to Arduino."""
    try:
        cmd = f"MOVE:{angle}\n"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)  # 5 second timeout
            s.connect((ARDUINO_IP, PORT))
            s.sendall(cmd.encode())
        print(f"✅ Sent command: {cmd.strip()}")
        return True
    except Exception as e:
        print(f"❌ Failed to send command: {e}")
        return False

def english_to_braille(text: str) -> list:
    """Convert English text to list of 6-bit Braille patterns."""
    # Simple Grade 1 Braille mapping (6-dot)
    braille_dict = {
        # Letters
        'a': '100000', 'b': '101000', 'c': '110000', 'd': '110100',
        'e': '100100', 'f': '111000', 'g': '111100', 'h': '101100',
        'i': '011000', 'j': '011100', 'k': '100010', 'l': '101010',
        'm': '110010', 'n': '110110', 'o': '100110', 'p': '111010',
        'q': '111110', 'r': '101110', 's': '011010', 't': '011110',
        'u': '100011', 'v': '101011', 'w': '011101', 'x': '110011',
        'y': '110111', 'z': '100111',
        
        # Numbers (prefix with # in Braille)
        '1': '100000', '2': '101000', '3': '110000', '4': '110100',
        '5': '100100', '6': '111000', '7': '111100', '8': '101100',
        '9': '011000', '0': '011100',

        # Basic punctuation
        '.': '010011', ',': '010000', '?': '011001', '!': '011010',
        '-': '001001', "'": '000010', ':': '010010', ';': '011000',
        ' ': '000000'  # space
    }

    # Optional: Braille number prefix
    NUMBER_PREFIX = '001111'
    CAPITAL_INDICATOR = '000001'

    braille_output = []
    for char in text:
        if char.isupper():
            # Capital prefix in Braille
            braille_output.append(CAPITAL_INDICATOR)
            char = char.lower()
        if char.isdigit():
            braille_output.append(NUMBER_PREFIX)
        braille_pattern = braille_dict.get(char, '000000')  # fallback to blank
        braille_output.append(braille_pattern)
    
    return braille_output

def braille_to_servo_angles(braille_pattern: str) -> list:
    """Convert 6-bit Braille pattern to servo angles for physical display.
    
    Maps each dot position to a servo angle:
    - 0 (dot down): 90 degrees
    - 1 (dot up): 110 degrees
    
    Braille cell layout:
    1 4
    2 5  
    3 6
    """
    angles = []
    for bit in braille_pattern:
        if bit == '1':
            angles.append(110)  # Dot up
        else:
            angles.append(90)   # Dot down
    return angles

def display_braille_on_arduino(braille_patterns: list, delay_between_chars: float = 1.0):
    """Display each Braille character on Arduino with delay between characters."""
    print(f"🔤 Displaying {len(braille_patterns)} Braille characters on Arduino...")
    
    for i, pattern in enumerate(braille_patterns):
        print(f"\n📍 Character {i+1}/{len(braille_patterns)}: Pattern '{pattern}'")
        
        # Convert Braille pattern to servo angles
        servo_angles = braille_to_servo_angles(pattern)
        
        # Send each servo position (assuming 6 servos for 6 dots)
        for servo_idx, angle in enumerate(servo_angles):
            print(f"   Servo {servo_idx+1}: {angle}°")
            # You might need to modify this based on your Arduino command protocol
            # This assumes the Arduino can handle individual servo commands
            success = send_servo_angle(angle)
            if not success:
                print(f"❌ Failed to set servo {servo_idx+1}")
            time.sleep(0.1)  # Small delay between servo movements
        
        # Wait before displaying next character
        if i < len(braille_patterns) - 1:  # Don't wait after the last character
            print(f"⏳ Waiting {delay_between_chars} seconds before next character...")
            time.sleep(delay_between_chars)
    
    print("✅ Braille display sequence completed!")

def form_brailles(text: str, display_delay: float = 1.0) -> dict[str, str]:
    """Main function: Convert English text to Braille and display on Arduino.
    
    Args:
        text: English text to convert and display
        display_delay: Delay in seconds between each Braille character
    
    Returns:
        Dictionary with conversion results and status
    """
    try:
        print(f"🔤 Converting text to Braille: '{text}'")
        
        # Convert English to Braille patterns
        braille_patterns = english_to_braille(text)
        braille_string = ' '.join(braille_patterns)
        
        print(f"📝 Braille patterns: {braille_string}")
        print(f"📊 Total characters to display: {len(braille_patterns)}")
        
        # Display on Arduino
        display_braille_on_arduino(braille_patterns, display_delay)
        
        return {
            "message": f"✅ Successfully converted and displayed '{text}' in Braille",
            "original_text": text,
            "braille_patterns": braille_patterns,
            "braille_string": braille_string,
            "character_count": len(braille_patterns)
        }
        
    except Exception as e:
        error_msg = f"❌ Error in Braille conversion/display: {e}"
        print(error_msg)
        return {"message": error_msg}

# Example usage and testing
if __name__ == "__main__":
    # Test the system
    test_text = "Hello"
    result = form_brailles(test_text, display_delay=1.0)
    print(f"\n🎯 Result: {result['message']}")
    
    # You can also test individual functions
    print(f"\n🧪 Testing individual conversion:")
    braille_patterns = english_to_braille("Hi")
    print(f"'Hi' in Braille: {' '.join(braille_patterns)}")
    
    # Test servo angle conversion
    test_pattern = "101100"  # Letter 'h'
    angles = braille_to_servo_angles(test_pattern)
    print(f"Pattern '{test_pattern}' servo angles: {angles}")