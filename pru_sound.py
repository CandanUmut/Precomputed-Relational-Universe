import numpy as np
import sounddevice as sd
import RPi.GPIO as GPIO
import time
import pickle
import os
from datetime import datetime

# ============= PRU DATABASE HANDLER =============

class PRUConstructor:
    def __init__(self, save_path="pru_db.pkl"):
        self.save_path = save_path
        self.database = []
        self.relational_map = {}
        self.load_database()

    def save_database(self):
        with open(self.save_path, "wb") as f:
            pickle.dump((self.database, self.relational_map), f)

    def load_database(self):
        if os.path.exists(self.save_path):
            with open(self.save_path, "rb") as f:
                self.database, self.relational_map = pickle.load(f)
        else:
            print("No existing PRU database found. Starting fresh.")

    def add_entry(self, entry):
        if entry not in self.relational_map:
            index = len(self.database)
            self.database.append(entry)
            self.relational_map[entry] = index
            self.save_database()

# ============= SENSOR CONFIGURATION =============

# GPIO setup
VIBRATION_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(VIBRATION_PIN, GPIO.IN)

# ============= SOUND PROCESSING =============

def record_sound(duration=1, fs=44100):
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    data = recording[:, 0]
    fft = np.fft.fft(data)
    freq = np.fft.fftfreq(len(fft), 1 / fs)
    idx = np.argmax(np.abs(fft))
    dominant_freq = abs(freq[idx])
    return round(dominant_freq, 2)

# ============= MAIN LOGGER LOOP =============

def main():
    pru = PRUConstructor()
    try:
        print("Starting sensor logging. Press Ctrl+C to stop.")
        while True:
            timestamp = datetime.utcnow().isoformat()

            # Sound
            sound_freq = record_sound()
            print(f"Sound Frequency: {sound_freq} Hz")

            # Vibration
            vibration = GPIO.input(VIBRATION_PIN)
            print(f"Vibration Detected: {bool(vibration)}")

            # Data entry
            entry = {
                "timestamp": timestamp,
                "sound_freq": sound_freq,
                "vibration": bool(vibration)
            }

            # Save into PRU DB
            pru.add_entry(str(entry))  # Convert dict to string for consistent hashable storage
            time.sleep(2)

    except KeyboardInterrupt:
        print("Logging stopped by user.")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
