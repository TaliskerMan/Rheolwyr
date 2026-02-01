import time
import threading
from pynput import keyboard
from pynput.keyboard import Key, KeyCode, Controller
import pyclip
from database import Database

class SnippetListener:
    def __init__(self):
        self.db = Database()
        self.buffer = ""
        self.max_buffer_size = 50
        self.keyboard_controller = Controller()
        self.listener = None
        self.running = False

    def start(self):
        if self.running:
            return
        self.running = True
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

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
        # 1. Backspace the trigger
        for _ in range(len(trigger)):
            self.keyboard_controller.tap(Key.backspace)
        
        # 2. Copy content to clipboard
        try:
            old_clipboard = pyclip.paste().decode('utf-8')
        except:
            old_clipboard = ""

        pyclip.copy(content)
        
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
