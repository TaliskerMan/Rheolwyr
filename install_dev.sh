#!/bin/bash
set -e

# This script installs the desktop file and icon to the user's local directory.
# This makes the app appear in the application menu with the correct icon.

echo "Installing Desktop file and Icon locally..."

# Install Desktop file
mkdir -p ~/.local/share/applications
cp data/com.taliskerman.rheolwyr.desktop ~/.local/share/applications/

# Install Icon
# Install Icon
mkdir -p ~/.local/share/icons/hicolor
cp -r data/icons/hicolor/* ~/.local/share/icons/hicolor/

# Update icon cache
echo "Updating icon cache..."
gtk-update-icon-cache ~/.local/share/icons/hicolor || true
update-desktop-database ~/.local/share/applications || true

echo "Installation complete!"
echo "If the icon still doesn't appear:"
echo "1. Press Alt+F2 and type 'r' to restart GNOME Shell (if on X11)"
echo "2. Log out and log back in (if on Wayland)"
