import serial
import time
import numpy as np
import sounddevice as sd
from threading import Thread

import mido
from mido import Message
import time
import math

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

                shifted_freq = current_freq * (2 ** ((pitch_shift * 2)/ 12))  # shift in semitones

                # Choose the IAC port (e.g., "IAC Driver Bus 1")
                outport = mido.open_output("IAC Driver Python MIDI")

                #TODO: Change velocity based on second input
                
                if shifted_freq > 0:
                    print("Shifted Frequency: ", shifted_freq)
                    # Send a note to GarageBand
                    outport.send(Message('note_on', note=freq_to_midi(shifted_freq), velocity=100))  
                    time.sleep(0.25)
                    outport.send(Message('note_off', note=freq_to_midi(shifted_freq), velocity=0))
                outport.send(Message('note_off', note=freq_to_midi(shifted_freq), velocity=0))

            except ValueError:
                continue
    finally:
        arduino.close()

def freq_to_midi(freq):
        print("Frequency: ", freq)

        if freq <= 0:
            print("Skip: Frequency must be positive.")
            freq = 10

        # TODO: Figure out why freq isnt positive
        return int(round(69 + 12 * math.log2(freq / 440.0)))

def main():
    # Print available MIDI ports
    print(mido.get_output_names())
    read_serial()

if __name__ == '__main__':
    main()

