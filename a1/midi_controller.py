import serial
import time
import numpy as np
import sounddevice as sd
from threading import Thread

import mido
from mido import Message
import time 
import subprocess
import time
import math

# Initial boolean state
prev_state = False  
current_state = True  
change_state = False

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
last_midi_note = None

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
    global current_state
    arduino = serial.Serial('/dev/tty.usbmodem1301', 19200, timeout=1)
    time.sleep(2)
    try:
        while True:
            line = arduino.readline().decode('utf-8').strip()
            print(line)
            dist = line.split(" ")[0]
            dist2 = line.split(" ")[1]
            ldr = line.split(" ")[2]

            print(dist + "" + dist2)
            try:
                distance = float(dist)
                current_freq = note_selector(distance)
                distance2 = float(dist2)
                ldr = float(ldr)

                if ldr <= 400:
                    current_state = True
                else:
                    current_state = False


                switch_track()
                shifted_freq = current_freq 
    
                vel = int(linear_scale(int(distance2), 0, 30, out_min=30, out_max=100))
                print("Velocity: " + str(vel))

                outport = mido.open_output("IAC Driver Python MIDI")

                if shifted_freq > 0:
                    print("Shifted Frequency: ", shifted_freq)
                    global last_midi_note
                    new_note = freq_to_midi(shifted_freq)

                    if new_note != last_midi_note:
                        if last_midi_note is not None:
                            outport.send(Message('note_off', note=last_midi_note, velocity=0))
                        outport.send(Message('note_on', note=new_note, velocity=vel))
                        last_midi_note = new_note
                else:
                    last_midi_note = 0

            except ValueError as e:
                print("Something bad happened", e)
                continue
    finally:
        arduino.close()

def freq_to_midi(freq):
        print("Frequency: ", freq)

        if freq <= 0:
            print("Skip: Frequency must be positive.")
            return None

        return int(round(69 + 12 * math.log2(freq / 440.0)))

def scaled_sigmoid(x, low=30, high=100):
    sig = 1 / (1 + np.exp(-x))
    return low + sig * (high - low)



def linear_scale(x, xmin, xmax, out_min=30, out_max=100):
    x = max(xmin, min(xmax, x))
    return out_min + ((x - xmin) / (xmax - xmin)) * (out_max - out_min)

def switch_track():
    global prev_state, current_state, change_state

    if current_state != prev_state:
        #if not change_state: 
        change_state = True
        #else:
        change_state = False
        if current_state:
            key_code = '125'  # Down Arrow
            direction = "down"
        else:
            key_code = '126'  # Up Arrow
            direction = "up"

        # run AppleScript
        script = f'''
        tell application "System Events"
            tell process "GarageBand"
                key code {key_code}
            end tell
        end tell
        '''
        subprocess.run(['osascript', '-e', script])
        print(f"Switched track {direction}")

    prev_state = current_state

    pass

def main():
    read_serial()

if __name__ == '__main__':
    main()

