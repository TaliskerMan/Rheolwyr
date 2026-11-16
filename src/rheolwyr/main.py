# Rheolwyr - Linux Text Expander
# Copyright (C) 2026 Chuck Talk <chuck@nordheim.online>
# Licensed under GPLv3 or later

import logging
from logging.handlers import RotatingFileHandler
import os
import signal
import sys

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Adw, Gio, GLib

from .listener import SnippetListener
from .window import RheolwyrWindow


class _SanitizingFormatter(logging.Formatter):
    """Sanitize CR/LF control characters from log messages (Log Sanitization rule)."""

    def format(self, record: logging.LogRecord) -> str:
        rendered = super().format(record)
        return rendered.replace("\r", "\\r").replace("\n", "\\n")


def setup_logging():
    """Configure application file logging under ~/.cache/rheolwyr/rheolwyr.log (0600, 5 MiB cap)."""
    log_dir = os.path.expanduser("~/.cache/rheolwyr")
    os.makedirs(log_dir, mode=0o700, exist_ok=True)
    os.chmod(log_dir, 0o700)
    log_file = os.path.join(log_dir, "rheolwyr.log")

    if not os.path.exists(log_file):
        try:
            fd = os.open(log_file, os.O_WRONLY | os.O_CREAT, 0o600)
            os.close(fd)
        except OSError:
            pass
    else:
        try:
            os.chmod(log_file, 0o600)
        except OSError:
            pass

    handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=2,
        encoding="utf-8",
    )
    handler.setFormatter(
        _SanitizingFormatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)


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
        except Exception as exception:
            logging.exception("Error starting listener")
            self.window.show_error_dialog(str(exception))

    def do_startup(self):
        """
        Configure theme styling and load core settings on startup.
        """
        Adw.Application.do_startup(self)
        # Verify theme usage (defaults to system preference, supporting light and dark)
        _ = Adw.StyleManager.get_default()


def main():
    """
    Bootstrap the application process, handle interrupts (SIGINT), and launch the loop.
    """
    setup_logging()
    GLib.set_prgname('com.taliskerman.rheolwyr')
    GLib.set_application_name('Rheolwyr')
    app = RheolwyrApp()
    # Handle Ctrl+C
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, app.quit)
    return app.run(sys.argv)


if __name__ == '__main__':
    main()
