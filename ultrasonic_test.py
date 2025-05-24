import serial
import time
import numpy as np
import sounddevice as sd

NOTE_C4 = 261.63
NOTE_D4 = 293.66
NOTE_E4 = 329.63
NOTE_F4 = 349.23
NOTE_G4 = 392.00
NOTE_A4 = 440.00

def main():
    # Replace '/dev/ttyACM0' with your Arduino port (e.g., 'COM3' on Windows)
    arduino = serial.Serial('/dev/tty.usbmodem21301', 19200, timeout=1)
    time.sleep(2)  # Wait for Arduino to initialize
    
    try:
        while True:
            line = arduino.readline().decode('utf-8').strip()
            note = line
            
            if line:
                distance = float(note)
                frequency = note_selector(distance)
                play_note(frequency, 0.1)
                        #40 * int(note.split('.')[0]), 0.05)

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        arduino.close()

def play_note(frequency=440.0, duration=1.0, sample_rate=19200):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    sd.play(wave, samplerate=sample_rate)
    sd.wait()

def note_selector(distance):
    if 0.0 <= distance <= 5.0:
        return NOTE_C4
    elif 5.0 < distance <= 10.0:
        return NOTE_D4
    elif 10.0 < distance <= 15.0:
        return NOTE_E4
    elif 15.0 < distance <= 20.0:
        return NOTE_F4
    elif 20.0 < distance <= 25.0:
        return NOTE_G4
    elif 25.0 < distance <= 30.0:
        return NOTE_A4
    else:
        return 0

if __name__ == '__main__':
    main()
