# Rheolwyr

Linux text expander.
Version 0.4.1
Rheolwyr ("Manager" in Welsh) is a Linux-native text snippet manager designed for Pop!_OS Cosmic and GNOME on Wayland.

## Features

- **Text Expansion**: Automatically expands keywords into snippets.
- **Global Shortcuts**: Trigger snippets from any application.
- **Split-View Editor**: Manage and edit snippets easily.
- **Theme persistence**: Remembers your preferred theme.
- **System Tray Support**: Runs in the background.
- **Wayland & X11 Support**: Designed with modern Linux desktop standards.

## Installation

1. Install system dependencies:

   ```bash
   sudo apt install libcairo2-dev libgirepository1.0-dev pkg-config python3-dev xclip wl-clipboard
   ```

2. Install python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:

   ```bash
   python -m rheolwyr.main
   # Or after pip install .
   rheolwyr
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
