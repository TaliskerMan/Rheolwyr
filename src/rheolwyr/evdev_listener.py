
import evdev
import select
import threading
import time
import sys

# Try to import pynput keys for compatibility
try:
    from pynput.keyboard import Key, KeyCode
except ImportError:
    Key = None
    KeyCode = None

class EvdevListener:
    def __init__(self, on_press=None):
        self.on_press = on_press
        self.running = False
        self.thread = None
        self._stop_event = threading.Event()
        
        # Modifier state
        self.modifiers = {
            'shift': False,
            'caps': False,
            'ctrl': False,
            'alt': False,
            'meta': False
        }

    def start(self):
        if self.running:
            return
            
        # Find keyboards
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        self.keyboards = []
        for dev in devices:
            cap = dev.capabilities()
            if evdev.ecodes.EV_KEY in cap:
                keys = cap[evdev.ecodes.EV_KEY]
                if evdev.ecodes.KEY_A in keys:
                    self.keyboards.append(dev)
        
        if not self.keyboards:
            print("EvdevListener: No keyboards found.")
            return

        print(f"EvdevListener: Listening on {len(self.keyboards)} devices.")
        self.running = True
        self._stop_event.clear()
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        self._stop_event.set()
        if self.thread:
            self.thread.join(timeout=1.0)

    def _run(self):
        # We need a map of FD -> Device
        fds = {dev.fd: dev for dev in self.keyboards}
        
        while self.running and not self._stop_event.is_set():
            try:
                r, w, x = select.select(fds, [], [], 0.5)
            except Exception as e:
                print(f"EvdevListener select error: {e}")
                break
                
            if not r:
                continue
                
            for fd in r:
                dev = fds.get(fd)
                if not dev: continue
                
                try:
                    for event in dev.read():
                        if event.type == evdev.ecodes.EV_KEY:
                            self._process_key(event)
                except OSError:
                    # Device lost
                    del fds[fd]

    def _process_key(self, event):
        # value 0=up, 1=down, 2=hold
        # We process on down (1) and hold (2) typically? 
        # pynput usually triggers on press (down).
        
        key_code = event.code
        val = event.value
        
        # Update modifiers
        if key_code in [evdev.ecodes.KEY_LEFTSHIFT, evdev.ecodes.KEY_RIGHTSHIFT]:
            self.modifiers['shift'] = (val > 0)
        elif key_code in [evdev.ecodes.KEY_LEFTCTRL, evdev.ecodes.KEY_RIGHTCTRL]:
            self.modifiers['ctrl'] = (val > 0)
        elif key_code in [evdev.ecodes.KEY_LEFTALT, evdev.ecodes.KEY_RIGHTALT]:
            self.modifiers['alt'] = (val > 0)
        elif key_code == evdev.ecodes.KEY_CAPSLOCK and val == 1:
            self.modifiers['caps'] = not self.modifiers['caps']
            
        if val == 1: # Key Press
            key_obj = self._map_key(key_code)
            if key_obj and self.on_press:
                try:
                    self.on_press(key_obj)
                except Exception as e:
                    print(f"Error in on_press: {e}")

    def _map_key(self, code):
        # Map evdev code to pynput Key or KeyCode
        
        # 1. Check for special keys
        special_map = {
            evdev.ecodes.KEY_BACKSPACE: Key.backspace,
            evdev.ecodes.KEY_TAB: Key.tab,
            evdev.ecodes.KEY_ENTER: Key.enter,
            evdev.ecodes.KEY_ESC: Key.esc,
            evdev.ecodes.KEY_SPACE: Key.space,
            evdev.ecodes.KEY_DELETE: Key.delete,
            evdev.ecodes.KEY_UP: Key.up,
            evdev.ecodes.KEY_DOWN: Key.down,
            evdev.ecodes.KEY_LEFT: Key.left,
            evdev.ecodes.KEY_RIGHT: Key.right,
            evdev.ecodes.KEY_HOME: Key.home,
            evdev.ecodes.KEY_END: Key.end,
            evdev.ecodes.KEY_PAGEUP: Key.page_up,
            evdev.ecodes.KEY_PAGEDOWN: Key.page_down,
            evdev.ecodes.KEY_LEFTSHIFT: Key.shift,
            evdev.ecodes.KEY_RIGHTSHIFT: Key.shift_r,
            evdev.ecodes.KEY_LEFTCTRL: Key.ctrl_l,
            evdev.ecodes.KEY_RIGHTCTRL: Key.ctrl_r,
            evdev.ecodes.KEY_LEFTALT: Key.alt_l,
            evdev.ecodes.KEY_RIGHTALT: Key.alt_r,
            evdev.ecodes.KEY_LEFTMETA: Key.cmd,
            evdev.ecodes.KEY_RIGHTMETA: Key.cmd,
            evdev.ecodes.KEY_CAPSLOCK: Key.caps_lock,
            evdev.ecodes.KEY_F1: Key.f1, evdev.ecodes.KEY_F2: Key.f2,
            evdev.ecodes.KEY_F3: Key.f3, evdev.ecodes.KEY_F4: Key.f4,
            evdev.ecodes.KEY_F5: Key.f5, evdev.ecodes.KEY_F6: Key.f6,
            evdev.ecodes.KEY_F7: Key.f7, evdev.ecodes.KEY_F8: Key.f8,
            evdev.ecodes.KEY_F9: Key.f9, evdev.ecodes.KEY_F10: Key.f10,
            evdev.ecodes.KEY_F11: Key.f11, evdev.ecodes.KEY_F12: Key.f12,
        }
        
        if code in special_map:
            return special_map[code]
            
        # 2. Check for char keys
        # Uses evdev key names to derive chars
        key_name = evdev.ecodes.keys.get(code)
        if isinstance(key_name, list): key_name = key_name[0]
        
        if not key_name or not isinstance(key_name, str):
            return None
            
        base_char = None
        if key_name.startswith('KEY_'):
            suffix = key_name[4:]
            if len(suffix) == 1 and suffix.isalpha():
                base_char = suffix.lower()
            elif suffix.isdigit():
                base_char = suffix
            elif suffix == 'MINUS': base_char = '-'
            elif suffix == 'EQUAL': base_char = '='
            elif suffix == 'LEFTBRACE': base_char = '['
            elif suffix == 'RIGHTBRACE': base_char = ']'
            elif suffix == 'SEMICOLON': base_char = ';'
            elif suffix == 'APOSTROPHE': base_char = "'"
            elif suffix == 'GRAVE': base_char = '`'
            elif suffix == 'BACKSLASH': base_char = '\\'
            elif suffix == 'COMMA': base_char = ','
            elif suffix == 'DOT': base_char = '.'
            elif suffix == 'SLASH': base_char = '/'
            
        if base_char:
            # Apply modifiers
            char = base_char
            shift = self.modifiers['shift']
            caps = self.modifiers['caps']
            
            if base_char.isalpha():
                if shift != caps:
                    char = base_char.upper()
            else:
                if shift:
                    # Symbol map
                    sym_map = {
                        '1':'!', '2':'@', '3':'#', '4':'$', '5':'%',
                        '6':'^', '7':'&', '8':'*', '9':'(', '0':')',
                        '-':'_', '=':'+', '[':'{', ']':'}',
                        ';':':', "'":'"', '`':'~', '\\':'|',
                        ',':'<', '.':'>', '/':'?'
                    }
                    char = sym_map.get(base_char, base_char)
            
            return KeyCode(char=char)
            
        return None
