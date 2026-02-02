import subprocess
import shutil

def is_wayland():
    import os
    return "WAYLAND_DISPLAY" in os.environ

def copy(text):
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
