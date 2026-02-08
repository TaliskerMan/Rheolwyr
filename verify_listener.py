
import time
import threading
import sys
import os

# Ensure we can import from src
sys.path.insert(0, os.path.abspath('src'))

from pynput import keyboard
from rheolwyr.uinput_controller import UInputController

# Global verification state
received_keys = []
stop_event = threading.Event()

def on_press(key):
    try:
        if hasattr(key, 'char') and key.char:
            received_keys.append(key.char)
        else:
            received_keys.append(str(key))
    except Exception as e:
        print(f"Error in on_press: {e}")

def run_listener():
    print("Starting pynput listener...")
    with keyboard.Listener(on_press=on_press) as listener:
        stop_event.wait()
        print("Stopping listener...")

def main():
    # 1. Start Listener in a thread
    t = threading.Thread(target=run_listener)
    t.start()
    
    # Give it time to start
    time.sleep(2)
    
    # 2. Inject keys via UInputController
    print("Injecting 'test' via UInputController...")
    try:
        controller = UInputController()
        # Ensure we have focus/time? 
        # Actually uinput injection is global, listener should hear it if it's working globally.
        for char in "test":
            controller.tap(char)
            time.sleep(0.1)
    except Exception as e:
        print(f"Injection failed: {e}")
        stop_event.set()
        t.join()
        sys.exit(1)

    # 3. Wait a bit
    time.sleep(1)
    stop_event.set()
    t.join()

    # 4. Check results
    print(f"Received keys: {received_keys}")
    expected = ['t', 'e', 's', 't']
    
    # We might receive more keys if there's noise, but we should at least see ours
    # Note: pynput might see 't', 'e', 's', 't' or KeyCode objects.
    
    # Simplified check
    data_str = "".join([str(k) for k in received_keys])
    if "test" in data_str or all(k in received_keys for k in expected):
        print("SUCCESS: pynput listener detected injected keys.")
        sys.exit(0)
    else:
        print("FAILURE: pynput listener did NOT detect keys.")
        sys.exit(1)

if __name__ == "__main__":
    main()
