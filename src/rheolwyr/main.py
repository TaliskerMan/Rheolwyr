# Rheolwyr - Linux Text Expander
# Copyright (C) 2026 Chuck Talk <cwtalk1@gmail.com>
# Licensed under GPLv3 or later

import sys
import gi
import signal

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, GLib
from .window import RheolwyrWindow
from .listener import SnippetListener

class RheolwyrApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id='com.taliskerman.rheolwyr',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.window = None
        self.listener = None

    def do_shutdown(self):
        if self.listener:
            self.listener.stop()
        Adw.Application.do_shutdown(self)

    def do_activate(self):
        if not self.window:
            self.window = RheolwyrWindow(self)
        self.window.present()
        
        # Start listener
        self.listener = SnippetListener()
        self.listener.start()

    def do_startup(self):
        Adw.Application.do_startup(self)
        # Verify theme usage
        style_manager = Adw.StyleManager.get_default()
        # This defaults to system preference, which supports both light and dark.


def main():
    app = RheolwyrApp()
    # Handle Ctrl+C
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, app.quit)
    return app.run(sys.argv)

if __name__ == '__main__':
    main()
