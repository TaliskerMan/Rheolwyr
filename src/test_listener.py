import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from listener import SnippetListener
# Now we can import real classes for typing/constants if needed, or mock them
from pynput.keyboard import Key

class TestListener(unittest.TestCase):
    def setUp(self):
        # Patch Database
        self.db_patcher = patch('listener.Database')
        self.mock_db_cls = self.db_patcher.start()
        self.mock_db = self.mock_db_cls.return_value
        
        # Patch pyclip
        self.pyclip_patcher = patch('listener.pyclip')
        self.mock_pyclip = self.pyclip_patcher.start()
        
        # Patch Controller
        self.controller_patcher = patch('listener.Controller')
        self.mock_controller_cls = self.controller_patcher.start()
        self.mock_controller = self.mock_controller_cls.return_value
        
        # Patch Listener (the pynput listener) to avoid starting a real thread
        self.keyboard_listener_patcher = patch('listener.keyboard.Listener')
        self.mock_keyboard_listener = self.keyboard_listener_patcher.start()
        
        self.listener = SnippetListener()
        self.listener.running = True

    def tearDown(self):
        self.db_patcher.stop()
        self.pyclip_patcher.stop()
        self.controller_patcher.stop()
        self.keyboard_listener_patcher.stop()

    def test_buffer_update(self):
        key = MagicMock()
        key.char = 'a'
        self.listener.on_press(key)
        self.assertEqual(self.listener.buffer, 'a')
        
        key.char = 'b'
        self.listener.on_press(key)
        self.assertEqual(self.listener.buffer, 'ab')

    def test_backspace(self):
        self.listener.buffer = "abc"
        self.listener.on_press(Key.backspace)
        self.assertEqual(self.listener.buffer, "ab")

    def test_trigger_match(self):
        self.listener.buffer = "test;sig"
        
        # Setup mock db
        self.mock_db.get_all_snippets.return_value = [
            (1, "Signature", "My Name", ";sig")
        ]
        
        # Mock expand_snippet
        with patch.object(self.listener, 'expand_snippet') as mock_expand:
            self.listener.check_match()
            mock_expand.assert_called_with(";sig", "My Name")
            self.assertEqual(self.listener.buffer, "")

    def test_expansion_logic(self):
        trigger = ";trig"
        content = "Expansion"
        
        self.listener.expand_snippet(trigger, content)
        
        # Verify backspaces (one tap per char)
        self.assertEqual(self.mock_controller.tap.call_count, len(trigger) + 1) # +1 for 'v'
        
        # Verify clipboard copy
        self.mock_pyclip.copy.assert_called_with(content)
        
        # Verify paste (ctrl+v)
        self.mock_controller.pressed.assert_called_with(Key.ctrl)
        # Verify 'v' was tapped (the last tap)
        self.mock_controller.tap.assert_called_with('v')

if __name__ == '__main__':
    unittest.main()
