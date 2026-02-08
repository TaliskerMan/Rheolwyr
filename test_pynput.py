
from pynput import keyboard
import time
import sys

def on_press(key):
    print(f"Key pressed: {key}")
    return False # Stop listener

print("Starting listener test...")
try:
    with keyboard.Listener(on_press=on_press) as listener:
        print("Listener started. Waiting for input (simulated or real)...")
        # We can't easily simulate input to ourselves if pynput input injection is also broken/restricted
        # But we can see if it crashes on start
        time.sleep(2)
        print("Listener running ok so far.")
except Exception as e:
    print(f"Listener failed: {e}")
