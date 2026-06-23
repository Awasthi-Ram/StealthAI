import mss
import sounddevice as sd
import soundfile as sf
from PIL import Image
import io
import time
import os

def capture_screen():
    """
    Captures the primary monitor screen and returns a PIL Image.
    """
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # 1 is the primary monitor
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            return img
    except Exception as e:
        print(f"Error capturing screen: {e}")
        return None

def record_audio(duration=5, fs=44100):
    """
    Records audio from the default microphone for `duration` seconds.
    Returns the path to the temporary wav file.
    """
    print(f"Recording audio for {duration} seconds...")
    try:
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()  # Wait until recording is finished
        
        temp_file = "temp_audio.wav"
        sf.write(temp_file, recording, fs)
        print("Audio recording complete.")
        return temp_file
    except Exception as e:
        print(f"Error recording audio: {e}")
        return None

def cleanup_audio(filepath):
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
        except:
            pass
