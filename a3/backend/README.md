# Smart Studio Backend

## Setup

1. Edit .env file with your OpenAI API key
2. Update SERIAL_PORT to match your Arduino port
3. Upload Arduino code to your board
4. Create a venv with `python -m venv venv`
5. Activate the venv with `source venv/bin/activate`
6. Install dependencies with `pip install -r requirements.txt`
7. Run the server with `python app.py`

To find your Arduino port:
- macOS: ls /dev/tty.usbmodem*
- Windows: Check Device Manager for COM ports
- Linux: ls /dev/ttyUSB* or ls /dev/ttyACM*