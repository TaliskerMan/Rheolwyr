import json
import os
from pathlib import Path
from gi.repository import Adw

APP_NAME = "rheolwyr"
CONFIG_DIR = Path.home() / ".config" / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "theme": "system"
}

def load_config():
    """Load configuration from JSON file."""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return DEFAULT_CONFIG.copy()

def save_config(data):
    """Save configuration to JSON file."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except OSError as e:
        print(f"Failed to save config: {e}")

def get_theme_scheme():
    """Get the Adw.ColorScheme based on stored config."""
    config = load_config()
    theme = config.get("theme", "system")
    
    if theme == "light":
        return Adw.ColorScheme.FORCE_LIGHT
    elif theme == "dark":
        return Adw.ColorScheme.FORCE_DARK
    else:
        return Adw.ColorScheme.DEFAULT

def set_theme_preference(scheme):
    """Save the theme preference based on the scheme enum."""
    config = load_config()
    
    if scheme == Adw.ColorScheme.FORCE_LIGHT:
        config["theme"] = "light"
    elif scheme == Adw.ColorScheme.FORCE_DARK:
        config["theme"] = "dark"
    else:
        config["theme"] = "system"
        
    save_config(config)
