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
        # We need to be careful not to delete too fast or too slow.
        for _ in range(len(trigger)):
            self.keyboard_controller.tap(Key.backspace)
            time.sleep(0.01) # Small delay to ensure backspaces register
        
        # 2. Inject content
        # Strategy: Use direct typing for short snippets (more reliable on Wayland)
        # Use clipboard for long snippets (faster)
        
        if len(content) < 50:
            print("Using direct typing for expansion")
            self.keyboard_controller.type(content)
        else:
            print("Using clipboard for expansion")
            # 2a. Copy content to clipboard
            try:
                # Save old clipboard if possible (best effort)
                old_clipboard = clipboard.paste().decode('utf-8')
            except:
                old_clipboard = ""

            clipboard.copy(content)
            
            # 2b. Paste
            # Simulating Ctrl+V
            # Note: In some terminals Ctrl+Shift+V is needed. This is hard to detect.
            # But standard GTK/Cosmic apps use Ctrl+V.
            time.sleep(0.1) # Wait for clipboard to update
            
            with self.keyboard_controller.pressed(Key.ctrl):
                self.keyboard_controller.tap('v')
                
            # Give it a moment, then restore clipboard?
            # Text expanders usually restore clipboard. 
            time.sleep(0.2) 
            if old_clipboard:
                 clipboard.copy(old_clipboard)
