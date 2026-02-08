import sys
import os
# Make sure we can import from src
src_path = os.path.abspath('src')
sys.path.insert(0, src_path)
print(f"Added {src_path} to sys.path")
import rheolwyr
print(f"Imported rheolwyr from: {rheolwyr.__file__}")

try:
    from rheolwyr.listener import SnippetListener
    from rheolwyr.uinput_controller import UInputController

    l = SnippetListener()
    print(f"Controller type: {type(l.keyboard_controller)}")
    print(f"Is instance of UInputController: {isinstance(l.keyboard_controller, UInputController)}")

    if isinstance(l.keyboard_controller, UInputController):
        print("SUCCESS: Listener is using UInputController")
        sys.exit(0)
    else:
        print("FAILURE: Listener is NOT using UInputController")
        sys.exit(1)
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
