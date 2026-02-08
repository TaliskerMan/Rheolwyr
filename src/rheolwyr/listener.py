import time
import threading
import os
from pynput import keyboard
from pynput.keyboard import Key, KeyCode, Controller as PynputController
from . import clipboard
from .database import Database
try:
    from .uinput_controller import UInputController
except ImportError:
    UInputController = None

class SnippetListener:
    def __init__(self):
        self.db = Database()
        self.buffer = ""
        self.max_buffer_size = 50
        # Prefer UInputController if available (for Wayland support)
        if UInputController:
            try:
                self.keyboard_controller = UInputController()
                print("Using UInputController for injection")
            except Exception as e:
                print(f"Failed to initialize UInputController: {e}")
                self.keyboard_controller = PynputController()
        else:
            self.keyboard_controller = PynputController()

try:
    from .evdev_listener import EvdevListener
except ImportError:
    EvdevListener = None

class SnippetListener:
    def __init__(self):
        self.db = Database()
        self.buffer = ""
        self.max_buffer_size = 50
        # Check for Wayland
        self.is_wayland = os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland" or os.environ.get("WAYLAND_DISPLAY")
        
        self.keyboard_controller = None
        
        # Prefer UInputController if available (for Wayland support)
        if self.is_wayland:
            if UInputController:
                try:
                    self.keyboard_controller = UInputController()
                    print("Using UInputController for injection")
                except Exception as e:
                    print(f"Failed to initialize UInputController: {e}")
                    # On Wayland, failure to get UInput means we likely can't inject.
                    # Raise error to notify user to check permissions.
                    raise PermissionError(f"Failed to initialize UInput: {e}\nPlease ensure you are in the 'uinput' group.")
            else:
                 raise ImportError("evdev not found. Please install python3-evdev.")
        else:
             # X11 fallback
             self.keyboard_controller = PynputController()

        self.listener = None
        self.running = False

    def start(self):
        if self.running:
            return
        self.running = True
        
        # Use EvdevListener if on Wayland and available
        if self.is_wayland:
            if EvdevListener:
                print("Starting EvdevListener (Wayland detected)...")
                try:
                    self.listener = EvdevListener(on_press=self.on_press)
                    self.listener.start()
                    
                    # Verify if listener actually found devices
                    # Wait a bit for thread to start?
                    # logic inside EvdevListener.start checks for keyboards.
                    # We might want EvdevListener to raise if no keyboards found.
                    if not self.listener.keyboards:
                         raise PermissionError("No keyboards detected. Please ensure you are in the 'input' group.")
                         
                    return
                except Exception as e:
                    print(f"Failed to start EvdevListener: {e}")
                    raise PermissionError(f"Failed to start Input Listener: {e}\nPlease ensure you are in the 'input' group.")
            else:
                 raise ImportError("evdev not found.")
        
        print("Starting pynput Listener...")
        try:
            self.listener = keyboard.Listener(on_press=self.on_press)
            self.listener.start()
        except Exception as e:
             print(f"Failed to start pynput Listener: {e}")

    def stop(self):
        if self.listener:
            self.listener.stop()
        self.running = False

    def on_press(self, key):
        if not self.running:
            return

        try:
            if hasattr(key, 'char') and key.char:
                self.buffer += key.char
            elif key == Key.space:
                self.buffer += " "
            elif key == Key.backspace:
                self.buffer = self.buffer[:-1]
            elif key == Key.enter:
                self.buffer = "" # Reset on enter usually
            else:
                # Other special keys might reset buffer or be ignored
                # For now let's not reset on shift/ctrl etc.
                pass
                
            # Trim buffer
            if len(self.buffer) > self.max_buffer_size:
                self.buffer = self.buffer[-self.max_buffer_size:]

            self.check_match()
        except Exception as e:
            print(f"Error in listener: {e}")

    def check_match(self):
        # We need to check if the *end* of the buffer matches any trigger.
        # This is a bit inefficient (checking all triggers on every keypress).
        # Optimization: Get all triggers once or cache them? 
        # For now, querying DB is safest for consistency, but maybe slow.
        # Let's optimize by getting all snippets triggers and checking in memory.
        # Since we are in the main thread (mostly), let's just query to be safe technically sqlite is fast enough for small DBs.
        # Use get_all_snippets()
        
        snippets = self.db.get_all_snippets()
        for s in snippets:
            # s: id, name, content, trigger
            trigger = s[3]
            if trigger and self.buffer.endswith(trigger):
                self.expand_snippet(trigger, s[2])
                self.buffer = "" # Reset buffer after expansion
                break

    def expand_snippet(self, trigger, content):
        print(f"DEBUG: Expanding snippet '{trigger}' -> '{content}'")
        # 1. Backspace the trigger
        for _ in range(len(trigger)):
            self.keyboard_controller.tap(Key.backspace)
        
        # 2. Copy content to clipboard
        # 2. Copy content to clipboard
        try:
            old_clipboard = clipboard.paste().decode('utf-8')
        except:
            old_clipboard = ""

        clipboard.copy(content)
        
        # 3. Paste
        # We need to be careful about shortcuts. Ctrl+V is standard for GUI.
        # Shift+Insert is standard for terminals.
        # This is tricky without knowing the target window.
        # Let's try sending keys directly first if it's short, or Ctrl+V if long?
        # The prompt mentioned "copy snippet to clipboard.. simulate paste"
        
        # Let's try typing it out if it's short, it's more reliable than paste usually
        # But for large snippets paste is better.
        # Let's assume paste for now as per plan "copy content to clipboard... simulate paste"
        
        # Simulating Ctrl+V
        with self.keyboard_controller.pressed(Key.ctrl):
            self.keyboard_controller.tap('v')
            
        # Give it a moment, then restore clipboard?
        # Text expanders usually restore clipboard. 
        # But this might be too complex for V1.
        time.sleep(0.1) 
