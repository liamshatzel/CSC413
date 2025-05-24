import serial
import time
import numpy as np
import sounddevice as sd
from threading import Thread

# Frequencies
NOTE_C4 = 261.63
NOTE_D4 = 293.66
NOTE_E4 = 329.63
NOTE_F4 = 349.23
NOTE_G4 = 392.00
NOTE_A4 = 440.00

# Audio settings
SAMPLE_RATE = 44100
current_freq = 0.0  # shared variable for current frequency
phase = 0.0         # persistent phase
pitch_shift = 0.0         # pitch shift in semitones

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
        return 0.0

def audio_callback(outdata, frames, time_info, status): 
    global phase
    t = (np.arange(frames) + phase) / SAMPLE_RATE

    shifted_freq = current_freq * (2 ** (pitch_shift / 12))  # shift in semitones
    wave = 0.5 * np.sin(2 * np.pi * shifted_freq * t)

    outdata[:] = wave.reshape(-1, 1).astype(np.float32)
    phase = (phase + frames) % SAMPLE_RATE  # wrap phase

def read_serial():
    global current_freq
    global pitch_shift
    arduino = serial.Serial('/dev/tty.usbmodem21301', 19200, timeout=1)
    time.sleep(2)
    try:
        while True:
            line = arduino.readline().decode('utf-8').strip()
            print(line)
            dist = line.split(" ")[0]
            pot = line.split(" ")[1]
            
            print(dist + " " + pot)
            try:
                distance = float(dist)
                current_freq = note_selector(distance)
                pot = float(pot)
                if pot >= 0 and pot <= 1023:
                    pitch_shift = (pot - 512) / 512 * 12  # Map to -12 to +12 semitones
                else:
                    pitch_shift = 0.0
            except ValueError:
                continue
    finally:
        arduino.close()

def main():
    # Start serial thread
    Thread(target=read_serial, daemon=True).start()

    # Start audio stream
    with sd.OutputStream(channels=1, samplerate=SAMPLE_RATE, callback=audio_callback):
        print("Streaming... Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting.")

if __name__ == '__main__':
    main()

