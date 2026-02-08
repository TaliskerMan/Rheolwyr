import time
from contextlib import contextmanager
try:
    import evdev
    from evdev import UInput, ecodes as e
except ImportError:
    evdev = None

class UInputController:
    """
    A controller that uses /dev/uinput to inject key events.
    This works on Wayland where XTest-based injection (pynput) fails.
    Requires user to be in 'input' or 'uinput' group and /dev/uinput to have correct permissions.
    """
    def __init__(self):
        if evdev is None:
            raise ImportError("evdev library is required for UInputController")
            
        # Define the capabilities of the virtual keyboard
        # We need to support all keys that might be typed or used for shortcuts
        cap = {
            e.EV_KEY: [
                e.KEY_A, e.KEY_B, e.KEY_C, e.KEY_D, e.KEY_E, e.KEY_F, e.KEY_G, 
                e.KEY_H, e.KEY_I, e.KEY_J, e.KEY_K, e.KEY_L, e.KEY_M, e.KEY_N, 
                e.KEY_O, e.KEY_P, e.KEY_Q, e.KEY_R, e.KEY_S, e.KEY_T, e.KEY_U, 
                e.KEY_V, e.KEY_W, e.KEY_X, e.KEY_Y, e.KEY_Z,
                e.KEY_1, e.KEY_2, e.KEY_3, e.KEY_4, e.KEY_5, e.KEY_6, e.KEY_7, 
                e.KEY_8, e.KEY_9, e.KEY_0,
                e.KEY_ENTER, e.KEY_BACKSPACE, e.KEY_TAB, e.KEY_SPACE,
                e.KEY_MINUS, e.KEY_EQUAL, e.KEY_LEFTBRACE, e.KEY_RIGHTBRACE,
                e.KEY_SEMICOLON, e.KEY_APOSTROPHE, e.KEY_GRAVE, e.KEY_BACKSLASH,
                e.KEY_COMMA, e.KEY_DOT, e.KEY_SLASH, e.KEY_CAPSLOCK,
                e.KEY_F1, e.KEY_F2, e.KEY_F3, e.KEY_F4, e.KEY_F5, e.KEY_F6, 
                e.KEY_F7, e.KEY_F8, e.KEY_F9, e.KEY_F10, e.KEY_F11, e.KEY_F12,
                e.KEY_HOME, e.KEY_END, e.KEY_PAGEUP, e.KEY_PAGEDOWN, 
                e.KEY_LEFT, e.KEY_RIGHT, e.KEY_UP, e.KEY_DOWN,
                e.KEY_LEFTSHIFT, e.KEY_RIGHTSHIFT, e.KEY_LEFTCTRL, e.KEY_RIGHTCTRL,
                e.KEY_LEFTALT, e.KEY_RIGHTALT, e.KEY_LEFTMETA, e.KEY_RIGHTMETA,
                e.KEY_ESC, e.KEY_DELETE, e.KEY_INSERT
            ]
        }
        
        try:
            self.ui = UInput(cap, name='Rheolwyr-UInput-Keyboard', version=0x1)
        except PermissionError:
            print("Error: Permission denied for /dev/uinput.")
            print("Please ensure you have run scripts/setup_permissions.sh and logged out/in.")
            raise

        # Mapping from pynput keys/chars to evdev ecodes
        self.char_map = {
            'a': e.KEY_A, 'b': e.KEY_B, 'c': e.KEY_C, 'd': e.KEY_D, 'e': e.KEY_E, 
            'f': e.KEY_F, 'g': e.KEY_G, 'h': e.KEY_H, 'i': e.KEY_I, 'j': e.KEY_J, 
            'k': e.KEY_K, 'l': e.KEY_L, 'm': e.KEY_M, 'n': e.KEY_N, 'o': e.KEY_O, 
            'p': e.KEY_P, 'q': e.KEY_Q, 'r': e.KEY_R, 's': e.KEY_S, 't': e.KEY_T, 
            'u': e.KEY_U, 'v': e.KEY_V, 'w': e.KEY_W, 'x': e.KEY_X, 'y': e.KEY_Y, 
            'z': e.KEY_Z,
            '1': e.KEY_1, '2': e.KEY_2, '3': e.KEY_3, '4': e.KEY_4, '5': e.KEY_5, 
            '6': e.KEY_6, '7': e.KEY_7, '8': e.KEY_8, '9': e.KEY_9, '0': e.KEY_0,
            '\n': e.KEY_ENTER, '\t': e.KEY_TAB, ' ': e.KEY_SPACE,
            '-': e.KEY_MINUS, '=': e.KEY_EQUAL, '[': e.KEY_LEFTBRACE, ']': e.KEY_RIGHTBRACE,
            ';': e.KEY_SEMICOLON, '\'': e.KEY_APOSTROPHE, '`': e.KEY_GRAVE, '\\': e.KEY_BACKSLASH,
            ',': e.KEY_COMMA, '.': e.KEY_DOT, '/': e.KEY_SLASH
        }
        
        # Upper case mapping (requires shift) - simplistic approach
        self.shift_chars = {
            'A': e.KEY_A, 'B': e.KEY_B, 'C': e.KEY_C, 'D': e.KEY_D, 'E': e.KEY_E,
            'F': e.KEY_F, 'G': e.KEY_G, 'H': e.KEY_H, 'I': e.KEY_I, 'J': e.KEY_J,
            'K': e.KEY_K, 'L': e.KEY_L, 'M': e.KEY_M, 'N': e.KEY_N, 'O': e.KEY_O,
            'P': e.KEY_P, 'Q': e.KEY_Q, 'R': e.KEY_R, 'S': e.KEY_S, 'T': e.KEY_T,
            'U': e.KEY_U, 'V': e.KEY_V, 'W': e.KEY_W, 'X': e.KEY_X, 'Y': e.KEY_Y,
            'Z': e.KEY_Z,
            '!': e.KEY_1, '@': e.KEY_2, '#': e.KEY_3, '$': e.KEY_4, '%': e.KEY_5,
            '^': e.KEY_6, '&': e.KEY_7, '*': e.KEY_8, '(': e.KEY_9, ')': e.KEY_0,
            '_': e.KEY_MINUS, '+': e.KEY_EQUAL, '{': e.KEY_LEFTBRACE, '}': e.KEY_RIGHTBRACE,
            ':': e.KEY_SEMICOLON, '"': e.KEY_APOSTROPHE, '~': e.KEY_GRAVE, '|': e.KEY_BACKSLASH,
            '<': e.KEY_COMMA, '>': e.KEY_DOT, '?': e.KEY_SLASH
        }

    def _get_keycode(self, key):
        """Resolves a key (char or pynput Key) to an evdev keycode and modifier requirement."""
        from pynput.keyboard import Key
        
        if hasattr(key, 'char') and key.char:
             char = key.char
             if char in self.char_map:
                 return self.char_map[char], False
             elif char in self.shift_chars:
                 return self.shift_chars[char], True
             else:
                 return None, False
        if isinstance(key, str):
             if len(key) == 1:
                 if key in self.char_map:
                     return self.char_map[key], False
                 elif key in self.shift_chars:
                     return self.shift_chars[key], True
             
        # Map common pynput Keys
        key_map = {
            Key.space: e.KEY_SPACE,
            Key.enter: e.KEY_ENTER,
            Key.backspace: e.KEY_BACKSPACE,
            Key.tab: e.KEY_TAB,
            Key.esc: e.KEY_ESC,
            Key.delete: e.KEY_DELETE,
            Key.up: e.KEY_UP,
            Key.down: e.KEY_DOWN,
            Key.left: e.KEY_LEFT,
            Key.right: e.KEY_RIGHT,
            Key.home: e.KEY_HOME,
            Key.end: e.KEY_END,
            Key.page_up: e.KEY_PAGEUP,
            Key.page_down: e.KEY_PAGEDOWN,
            Key.shift: e.KEY_LEFTSHIFT, # Default to left
            Key.ctrl: e.KEY_LEFTCTRL,
            Key.alt: e.KEY_LEFTALT,
            Key.cmd: e.KEY_LEFTMETA,
            Key.caps_lock: e.KEY_CAPSLOCK,
             # Add other mappings as needed
            'v': e.KEY_V, # Special case for ctrl+v string arg
        }
        
        if key in key_map:
            return key_map[key], False
            
        return None, False

    def tap(self, key):
        """Press and release a key."""
        ecode, need_shift = self._get_keycode(key)
        if ecode:
            if need_shift:
                self.ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
                self.ui.syn()
                
            self.ui.write(e.EV_KEY, ecode, 1)
            self.ui.syn()
            self.ui.write(e.EV_KEY, ecode, 0)
            self.ui.syn()
            
            if need_shift:
                self.ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
                self.ui.syn()
                
            time.sleep(0.01) # Small delay to let input propagate

    @contextmanager
    def pressed(self, key):
        """Context manager to hold a key down."""
        ecode, _ = self._get_keycode(key)
        if ecode:
            self.ui.write(e.EV_KEY, ecode, 1)
            self.ui.syn()
            try:
                yield
            finally:
                self.ui.write(e.EV_KEY, ecode, 0)
                self.ui.syn()
                time.sleep(0.01)

    def type(self, text):
        """Type a string of characters."""
        for char in text:
            self.tap(char)
