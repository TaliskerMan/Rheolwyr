# Copyright (C) 2026 Chuck Talk <chuck@nordheim.online>
# This file is part of Rheolwyr.
#
# Rheolwyr is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, version 3.
#
# Rheolwyr is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY. See the GNU GPL v3 for details.

"""
Listener module for handling keyboard input and snippet expansion.

Privacy note: this module is, by necessity, in the keystroke path. It keeps an
in-memory "current word" buffer only (capped, reset on word boundaries and
navigation) and NEVER logs raw keystrokes or expanded snippet content. Debug
logging is via the standard ``logging`` module and is silent unless the operator
explicitly raises the level; even then it logs only trigger lengths/metadata,
not snippet bodies.
"""
import logging
import os
import time

from . import clipboard
from .database import Database
from .matching import find_trigger
from ag_gtk_utils.listener import BaseListener

logger = logging.getLogger(__name__)

try:
    from pynput import keyboard
    from pynput.keyboard import Controller as PynputController
    from pynput.keyboard import Key, KeyCode
except ImportError:
    keyboard = None
    PynputController = None
    class Key:
        space = "space"
        backspace = "backspace"
        enter = "enter"
        tab = "tab"
        ctrl = "ctrl"
    class KeyCode:
        def __init__(self, char=None):
            self.char = char

try:
    from .uinput_controller import UInputController
except ImportError:
    UInputController = None


try:
    from .evdev_listener import EvdevListener
except ImportError:
    EvdevListener = None


# Keys that complete a word and may therefore trigger an expansion of the word
# just typed. Keeping this to whitespace makes expansion predictable and avoids
# firing a trigger in the middle of a longer word (e.g. "addr" inside
# "address").
_DELIMITER_KEYS = {Key.space: " ", Key.tab: "\t"}

# Keys that invalidate the buffer because they move the cursor or change focus,
# so the in-memory buffer can no longer be trusted to mirror the real text.
_RESET_KEYS = {
    getattr(Key, name, None)
    for name in (
        "enter", "esc", "up", "down", "left", "right",
        "home", "end", "page_up", "page_down", "delete",
    )
}
_RESET_KEYS.discard(None)


class SnippetListener(BaseListener):
    """
    Main controller for keyboard event capturing and snippet substitution.
    """
    def __init__(self):
        """
        Initialize the database handle, state trackers, and the correct keyboard injection controller.

        Selects UInputController on Wayland and PynputController on X11 fallback.
        """
        self.db = Database()
        self.buffer = ""
        self.max_buffer_size = 50

        # In-memory trigger cache (P1-6): avoid querying the DB on every
        # keystroke. Refreshed via refresh_snippets() when the snippet set
        # changes. Maps trigger -> content.
        self._triggers = {}

        # Self-injection guard (P1-5): ignore input while we are injecting, and
        # for a short settle window afterwards, so the characters we type (and
        # the simulated Ctrl+V) are not read back into the buffer.
        self._injecting = False
        self._suppress_until = 0.0

        # Check for Wayland
        self.is_wayland = os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland" or os.environ.get("WAYLAND_DISPLAY")

        self.keyboard_controller = None

        # Prefer UInputController if available (for Wayland support)
        if self.is_wayland:
            if UInputController:
                try:
                    self.keyboard_controller = UInputController()
                    logger.info("Using UInputController for injection")
                except Exception as exception:
                    logger.error("Failed to initialize UInputController: %s", exception)
                    # On Wayland, failure to get UInput means we likely can't inject.
                    # Raise error to notify user to check permissions.
                    raise PermissionError(f"Failed to initialize UInput: {exception}\nPlease ensure you are in the 'uinput' group.")
            else:
                raise ImportError("evdev not found. Please install python3-evdev.")
        else:
            # X11 fallback
            self.keyboard_controller = PynputController()

        self.listener = None
        self.running = False
        self.refresh_snippets()

    def refresh_snippets(self):
        """
        Reload the in-memory trigger cache from the database.

        Call this whenever snippets are added, edited, deleted, or imported so
        the listener matches the current set without querying SQLite on every
        keypress.
        """
        try:
            snippets = self.db.get_all_snippets()
            # s: id, name, content, trigger
            self._triggers = {
                s[3]: s[2] for s in snippets if s[3]
            }
            logger.debug("Trigger cache refreshed: %d trigger(s)", len(self._triggers))
        except Exception:
            logger.exception("Failed to refresh trigger cache")

    def start(self):
        """
        Start the background event listener thread.
        """
        if self.running:
            return
        self.running = True

        # Use EvdevListener if on Wayland and available
        if self.is_wayland:
            if EvdevListener:
                logger.info("Starting EvdevListener (Wayland detected)...")
                try:
                    self.listener = EvdevListener(on_press=self.on_press)
                    self.listener.start()

                    # Verify the listener actually found devices.
                    if not self.listener.keyboards:
                        raise PermissionError("No keyboards detected. Please ensure you are in the 'input' group.")

                    return
                except Exception as exception:
                    logger.error("Failed to start EvdevListener: %s", exception)
                    raise PermissionError(f"Failed to start Input Listener: {exception}\nPlease ensure you are in the 'input' group.")
            else:
                raise ImportError("evdev not found.")

        logger.info("Starting pynput Listener...")
        try:
            self.listener = keyboard.Listener(on_press=self.on_press)
            self.listener.start()
        except Exception as exception:
            logger.error("Failed to start pynput Listener: %s", exception)

    def stop(self):
        """
        Stop the active input listener.
        """
        if self.listener:
            self.listener.stop()
        self.running = False

    def on_press(self, key):
        """
        Handle a keypress: maintain the in-memory word buffer and check for instant trigger expansion.

        Buffer rules: printable characters extend the buffer and trigger immediate
        expansion checks (CP-ChangeComments: Instant trigger matching on keypress without space/tab);
        delimiters and navigation keys update or reset the buffer as appropriate.
        """
        if not self.running:
            return

        # Ignore self-injected events (P1-5).
        if self._injecting or time.time() < self._suppress_until:
            return

        try:
            if key in _DELIMITER_KEYS:
                self.buffer += _DELIMITER_KEYS[key]
                if self._try_expand():
                    return
            elif key == Key.backspace:
                self.buffer = self.buffer[:-1]
            elif key in _RESET_KEYS:
                # Cursor moved or line submitted; buffer can no longer be trusted.
                self.buffer = ""
                return
            elif hasattr(key, 'char') and key.char:
                self.buffer += key.char
                if self._try_expand():
                    return
            else:
                # Modifiers and other non-text keys: leave buffer unchanged.
                return

            # Trim buffer to the most recent characters.
            if len(self.buffer) > self.max_buffer_size:
                self.buffer = self.buffer[-self.max_buffer_size:]
        except Exception:
            logger.exception("Error handling keypress")

    def _try_expand(self):
        """
        If the end of the buffer matches a registered trigger, expand it immediately.
        Returns True if an expansion was performed.
        """
        trigger = find_trigger(self.buffer, self._triggers)
        if trigger is None:
            return False
        self.expand_snippet(trigger, self._triggers[trigger])
        self.buffer = ""
        return True

    def expand_snippet(self, trigger, content):
        """
        Replace the trigger text with the expanded snippet content.

        Deletes the trigger characters and injects the content (direct typing for
        short snippets, clipboard paste for long ones) via the selected keyboard
        controller. Input is suppressed during and shortly after injection so the
        synthetic keystrokes are not read back into the buffer.
        """
        logger.debug("Expanding trigger of length %d -> %d char(s)", len(trigger), len(content))

        self._injecting = True
        try:
            # Wait for physical keys to be released to avoid Wayland dropping
            # injected keys.
            if hasattr(self.listener, 'pressed_keys'):
                for _ in range(50):
                    if not self.listener.pressed_keys:
                        break
                    time.sleep(0.01)

            # 1. Backspace the trigger.
            for _ in range(len(trigger)):
                self.keyboard_controller.tap(Key.backspace)
                time.sleep(0.01)

            # 2. Inject content. Direct typing is more reliable on Wayland for
            #    short snippets; clipboard paste is faster for long ones.
            if len(content) < 50:
                self.keyboard_controller.type(content)
            else:
                self._paste_content(content)
        finally:
            # Hold the suppression window open briefly so queued synthetic
            # events (read after this call returns) are ignored.
            self._suppress_until = time.time() + 0.3
            self._injecting = False

    def _paste_content(self, content):
        """
        Inject long content via the clipboard, preserving the user's previous
        clipboard where it is text. Binary clipboards (e.g. images) are not
        decoded or restored, to avoid corruption.
        """
        old_clipboard = None
        try:
            raw = clipboard.paste()
            try:
                old_clipboard = raw.decode('utf-8')
            except (UnicodeDecodeError, AttributeError):
                # Non-text clipboard (image, etc.): do not attempt to restore it.
                old_clipboard = None
        except Exception:
            logger.debug("Could not read existing clipboard; not restoring", exc_info=True)

        clipboard.copy(content)
        time.sleep(0.1)  # Allow the clipboard to update before pasting.

        with self.keyboard_controller.pressed(Key.ctrl):
            self.keyboard_controller.tap('v')

        # Give the paste time to complete before restoring the old clipboard.
        if old_clipboard:
            time.sleep(0.2)
            clipboard.copy(old_clipboard)
