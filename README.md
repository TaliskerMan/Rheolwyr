# Rheolwyr

Rheolwyr ("Manager" in Welsh) is a Linux-native text snippet manager designed for Pop!_OS Cosmic and GNOME on Wayland.

## Features
- **Global Shortcuts**: Trigger snippets from any application.
- **Split-View Editor**: Manage and edit snippets easily.
- **System Tray Support**: Runs in the background.
- **Wayland Native**: Designed with modern Linux desktop standards.

## Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python src/main.py
   ```

## Tech Stack
- Python 3
- GTK4 + Libadwaita
- SQLite

## Packaging

### Debian / Ubuntu
Build using `dpkg-buildpackage`:
```bash
dpkg-buildpackage -us -uc
```

### Flatpak
Build using `flatpak-builder`:
```bash
flatpak-builder --user --install build-dir com.taliskerman.rheolwyr.yml
```

## License
GPLv3
