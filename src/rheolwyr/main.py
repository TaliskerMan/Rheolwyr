# Rheolwyr - Linux Text Expander
# Copyright (C) 2026 Chuck Talk <cwtalk1@gmail.com>
# Licensed under GPLv3 or later

import signal
import sys

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Adw, Gio, GLib

from .listener import SnippetListener
from .window import RheolwyrWindow


class RheolwyrApp(Adw.Application):
    """
    Main Libadwaita Application class orchestrating the window manager and input listener.
    """
    def __init__(self):
        """
        Initialize the application ID and setup flags.
        """
        super().__init__(application_id='com.taliskerman.rheolwyr',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.window = None
        self.listener = None

    def do_shutdown(self):
        """
        Clean up resources, stop background listeners, and terminate the application context.
        """
        if self.listener:
            self.listener.stop()
        Adw.Application.do_shutdown(self)

    def do_activate(self):
        """
        Triggered when the app is activated; mounts the main window and initializes listeners.
        """
        if not self.window:
            self.window = RheolwyrWindow(self)
        self.window.present()

        # Start listener
        try:
            self.listener = SnippetListener()
            self.listener.start()
        except Exception as e:
            print(f"Error starting listener: {e}")
            self.window.show_error_dialog(str(e))

    def do_startup(self):
        """
        Configure theme styling and load core settings on startup.
        """
        Adw.Application.do_startup(self)
        # Verify theme usage
        style_manager = Adw.StyleManager.get_default()
        # This defaults to system preference, which supports both light and dark.


def main():
    """
    Bootstrap the application process, handle interrupts (SIGINT), and launch the loop.
    """
    GLib.set_prgname('com.taliskerman.rheolwyr')
    GLib.set_application_name('Rheolwyr')
    app = RheolwyrApp()
    # Handle Ctrl+C
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, app.quit)
    return app.run(sys.argv)

if __name__ == '__main__':
    main()
