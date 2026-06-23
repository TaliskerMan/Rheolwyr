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
Application Configuration and Theme Preferences Module.

Loads and saves user configuration preferences from/to config.json
and provides Libadwaita color scheme translators.
"""

import json
from pathlib import Path

from gi.repository import Adw

APP_NAME = "rheolwyr"
CONFIG_DIR = Path.home() / ".config" / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "theme": "system"
}

def load_config():
    """
    Load configuration parameters from the local configuration file.
    
    Falls back to default configurations on parsing failure or missing files.
    """
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return DEFAULT_CONFIG.copy()

def save_config(data):
    """
    Save the given configuration data dictionary to config.json.
    """
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except OSError as e:
        print(f"Failed to save config: {e}")

def get_theme_scheme():
    """
    Resolve the Adw.ColorScheme enum matching the stored theme configuration.
    """
    config = load_config()
    theme = config.get("theme", "system")

    if theme == "light":
        return Adw.ColorScheme.FORCE_LIGHT
    elif theme == "dark":
        return Adw.ColorScheme.FORCE_DARK
    else:
        return Adw.ColorScheme.DEFAULT

def set_theme_preference(scheme):
    """
    Save the user theme preference derived from a Libadwaita ColorScheme enum.
    """
    config = load_config()

    if scheme == Adw.ColorScheme.FORCE_LIGHT:
        config["theme"] = "light"
    elif scheme == Adw.ColorScheme.FORCE_DARK:
        config["theme"] = "dark"
    else:
        config["theme"] = "system"

    save_config(config)
