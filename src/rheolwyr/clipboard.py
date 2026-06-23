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
Clipboard Integration Utilities.

Provides Wayland and X11 clipboard access via wl-clipboard or xclip
for expanding snippets and recovering the original clipboard state.
"""

import shutil
import subprocess

def is_wayland():
    """
    Check if the active desktop session is running under Wayland.
    """
    import os
    return "WAYLAND_DISPLAY" in os.environ or os.environ.get("XDG_SESSION_TYPE") == "wayland"

def copy(text):
    """
    Copy utf-8 text content to the clipboard.
    
    Tries wl-copy on Wayland, and falls back to xclip.
    """
    text_bytes = text.encode('utf-8')
    if is_wayland():
        if shutil.which("wl-copy"):
            try:
                subprocess.run(["wl-copy"], input=text_bytes, check=True)
                return
            except subprocess.CalledProcessError:
                pass

    # Fallback to xclip or if not wayland
    if shutil.which("xclip"):
        try:
            subprocess.run(["xclip", "-selection", "clipboard"], input=text_bytes, check=True)
        except subprocess.CalledProcessError:
            pass

def paste():
    """
    Paste raw byte contents from the system clipboard.
    """
    if is_wayland():
        if shutil.which("wl-paste"):
            try:
                result = subprocess.run(["wl-paste"], capture_output=True, check=True)
                return result.stdout
            except subprocess.CalledProcessError:
                pass

    if shutil.which("xclip"):
        try:
            result = subprocess.run(["xclip", "-selection", "clipboard", "-o"], capture_output=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError:
            pass

    return b""
