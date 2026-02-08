
import time
import threading
import sys
import os

# Ensure we can import from src
src_path = os.path.abspath('src')
sys.path.insert(0, src_path)

from rheolwyr.listener import SnippetListener
from rheolwyr.uinput_controller import UInputController

def main():
    print("Initializing SnippetListener...")
    listener = SnippetListener()
    
    # Check what listener implementation is used
    if hasattr(listener, 'is_wayland') and listener.is_wayland:
        print("Mode: Wayland detected.")
        import evdev
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        print(f"Debug: Found {len(devices)} evdev devices:")
        for dev in devices:
            print(f" - {dev.name} ({dev.path})")
            cap = dev.capabilities()
            if evdev.ecodes.EV_KEY in cap:
                print(f"   Has EV_KEY. Keys: {len(cap[evdev.ecodes.EV_KEY])}")
                if evdev.ecodes.KEY_A in cap[evdev.ecodes.EV_KEY]:
                    print("   Has KEY_A")
                else:
                    print("   MISSING KEY_A")
            else:
                print("   No EV_KEY")
    else:
        print("Mode: X11/Other.")
        
    listener.start()
    print(f"Listener started. Type: {type(listener.listener)}")
    
    # Give it time to start and find devices
    time.sleep(2)
    
    # Inject keys
    target_string = "test"
    print(f"Injecting '{target_string}'...")
    
    try:
        controller = UInputController()
        for char in target_string:
            controller.tap(char)
            time.sleep(0.1)
    except Exception as e:
        print(f"Injection failed: {e}")
        listener.stop()
        sys.exit(1)
        
    time.sleep(1)
    
    print(f"Buffer content: '{listener.buffer}'")
    
    if target_string in listener.buffer:
        print("SUCCESS: Input detected and buffer updated.")
        listener.stop()
        sys.exit(0)
    else:
        print("FAILURE: Input NOT detected in buffer.")
        listener.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
