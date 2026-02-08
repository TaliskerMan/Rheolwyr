#!/bin/bash
set -e

echo "Setting up permissions for Rheolwyr text expansion on Wayland..."


# 0. Install dependencies
echo "Installing dependencies..."
if command -v apt &> /dev/null; then
    sudo apt update
    sudo apt install -y python3-evdev python3-pynput python3-gi python3-full
elif command -v dnf &> /dev/null; then
    sudo dnf install -y python3-evdev python3-pynput python3-gobject
elif command -v pacman &> /dev/null; then
    sudo pacman -S --noconfirm python-evdev python-pynput python-gobject
else
    echo "Could not detect package manager. Please install 'python3-evdev' manually."
fi

# 1. Create uinput group if it doesn't exist
if ! getent group uinput >/dev/null; then
    echo "Creating 'uinput' group..."
    sudo groupadd uinput
fi

# 2. Add user to input and uinput groups
echo "Adding user '$USER' to 'input' and 'uinput' groups..."
sudo usermod -aG input $USER
sudo usermod -aG uinput $USER

# 3. Create udev rule for uinput
echo "Creating udev rule for /dev/uinput..."
echo 'KERNEL=="uinput", GROUP="uinput", MODE="0660"' | sudo tee /etc/udev/rules.d/99-rheolwyr-uinput.rules > /dev/null

# 4. Reload udev rules
echo "Reloading udev rules..."
sudo udevadm control --reload-rules
sudo udevadm trigger

echo "Done! You must LOG OUT and LOG BACK IN for these changes to take effect."
