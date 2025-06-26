import os
import time
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
import serial
import openai
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load environment variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
SERIAL_PORT = os.environ.get('SERIAL_PORT', '/dev/tty.usbmodem1101')
BAUD_RATE = int(os.environ.get('BAUD_RATE', 9600))

# Debug: Print environment status
print(f"Environment check:")
print(f"  OPENAI_API_KEY: {'Set' if OPENAI_API_KEY else 'NOT SET'}")
print(f"  SERIAL_PORT: {SERIAL_PORT}")
print(f"  BAUD_RATE: {BAUD_RATE}")

# Check OpenAI API key
if OPENAI_API_KEY:
    print("OpenAI API key configured")
else:
    print("WARNING: OpenAI API key not configured - chat functionality will not work")

# Initialize serial port
ser = None
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    serial_connected = True
except Exception as e:
    print(f"Failed to open serial port: {e}")
    serial_connected = False

# Store latest sensor readings
data_lock = threading.Lock()
latest_sensor = {
    'temperature': 0,
    'humidity': 0,
}

def serial_reader():
    global latest_sensor
    if not ser:
        return
    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            if line:
                if line.startswith('data:'):
                    parts = line[5:].strip().split()
                    if len(parts) == 2:
                        try:
                            temp = int(parts[0])
                            hum = int(parts[1])
                            with data_lock:
                                latest_sensor['temperature'] = temp 
                                latest_sensor['humidity'] = hum 
                        except ValueError:
                            pass
        except Exception as e:
            print(f"Serial read error: {e}")
            time.sleep(1)

# Start serial reader thread
if ser:
    t = threading.Thread(target=serial_reader, daemon=True)
    t.start()

def send_to_arduino(command):
    if ser and ser.is_open:
        ser.write((command + '\n').encode('utf-8'))
        print(f"Sent to Arduino: {command}")
    else:
        print(f"Serial port not available, command would be: {command}")

def parse_response(response):
    """Parse response to extract RGB and fan values from JSON format"""
    try:
        # Try to parse as JSON first
        data = json.loads(response)
        if 'r' in data and 'g' in data and 'b' in data and 'fan' in data:
            r = data['r'] if data['r'] is not None and data['r'] != "" else 0
            g = data['g'] if data['g'] is not None and data['g'] != "" else 0
            b = data['b'] if data['b'] is not None and data['b'] != "" else 0
            fan = data['fan'] if data['fan'] is not None and data['fan'] != "" else 0

            # Convert to int, with fallback to 0 if conversion fails
            try:
                r = int(r)
            except (ValueError, TypeError):
                r = 0
            try:
                g = int(g)
            except (ValueError, TypeError):
                g = 0
            try:
                b = int(b)
            except (ValueError, TypeError):
                b = 0
            try:
                fan = int(fan)
            except (ValueError, TypeError):
                fan = 0
            
            # Constrain values to 0-255
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            fan = max(0, min(255, fan))
            return [f"{r},{g},{b},{fan}"]
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        print(f"Failed to parse response: {e}")
        print(f"Response was: {response}")
    return []

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json()
    message = data.get('msg')  # Changed from 'message' to 'msg' to match frontend
    temp = data.get('temp', '0')
    humidity = data.get('humidity', '0')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Check if OpenAI API key is configured
    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY is not set")
        return jsonify({'error': 'OpenAI API key not configured'}), 500
    
    try:
        # Create the full message with sensor data
        full_message = f"{{msg: \"{message}\", temp: \"{temp}\", humidity: \"{humidity}\"}}"
        
        print(f"Making OpenAI request with message: {full_message}")
        
        # Use the current OpenAI client syntax
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": 
                """You are a tool which helps artists brainstorm their next art piece, by supporting their creative environment. 
                You are to respond to following prompts giving inspiration to the artist, but you should never tell the artist how to do their art, you should simply give inspiring background, related activities, tips on working with the medium, or related works. You are to respond in the following JSON format:
                {
                "artist_response": "",
                "reasoning": "",
                "r": "",
                "g": "",
                "b": "",
                "fan": ""
                } 
                Where artist_response is the inspiration you would give to the artist, it should be in plain text with no markdown. 
                RGB are RGB LED values in the range from 0-255. You should choose the RGB LED values based on the mood of the inspiration the artist is asking for (i.e. a warm art piece could be a warm yellow), you should make the RGB values vibrant. Fan will also be in the range from 0-255 and should be based on the temperature and humidity of the room, along with the sentiment of the piece. (i.e. an emotionally cold piece should have the fan on). My input to you will be in the JSON form of: {msg: "artist message",  temp: "", humidity: ""}. Temperature and humidity of the artist studio will be given by the user. Make the RGB and fan values diverse, give a reason to why you set the RGB (translated to color) and fan value in the reasoning field, do not mention the number values you set them to, but rather the color or speed instead. 
                To respond that you've understood this message simply reply with the given JSON and none values.
                """},
                {"role": "user", "content": full_message}
            ],
            max_tokens=300
        )
        response = completion.choices[0].message.content
        
        print(f"OpenAI response: {response}")
        
        # Parse the response to extract the artist_response for display
        try:
            response_data = json.loads(response)
            artist_response = response_data.get('artist_response', response)
            reasoning = response_data.get('reasoning', '')
            
            # Combine artist response and reasoning
            if reasoning:
                full_response = f"{artist_response}\n\n---\n\n**Why this environment?** {reasoning}"
            else:
                full_response = artist_response
                
        except json.JSONDecodeError as e:
            print(f"Failed to parse OpenAI response as JSON: {e}")
            full_response = response
        
        arduino_commands = parse_response(response)
        for command in arduino_commands:
            send_to_arduino(command)
        
        return jsonify({
            'response': full_response,
            'commands': arduino_commands
        })
    except Exception as e:
        print(f"Unexpected error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({
        'status': 'ok',
        'serialConnected': ser.is_open if ser else False
    })

@app.route('/api/sensor', methods=['GET'])
def api_sensor():
    with data_lock:
        return jsonify({
            'temperature': latest_sensor['temperature'],
            'humidity': latest_sensor['humidity']
        })

@app.route('/api/control', methods=['POST'])
def api_control():
    data = request.get_json()
    r = data.get('r')
    g = data.get('g')
    b = data.get('b')
    fan = data.get('fan')
    errors = []
    for v, name in zip([r, g, b, fan], ['r', 'g', 'b', 'fan']):
        if not isinstance(v, int):
            errors.append(f'{name} must be an integer')
        elif not (0 <= v <= 255):
            errors.append(f'{name} must be between 0 and 255')
    if errors:
        return jsonify({'error': '; '.join(errors)}), 400
    send_to_arduino(f"{r},{g},{b},{fan}")
    return jsonify({'message': 'RGB and fan values sent', 'r': r, 'g': g, 'b': b, 'fan': fan})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True) 