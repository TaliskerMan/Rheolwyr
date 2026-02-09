# Rheolwyr Walkthrough

Rheolwyr is a text expander for Linux (GNOME/Cosmic).

## Features
- **Text Expansion**: Types out your snippets when you type a trigger keyword.
- **Wayland Support**: Uses `uinput` for reliable injection on Wayland.
- **Clipboard Fallback**: Uses clipboard for large snippets.

## Usage

1. **Start Rheolwyr**:
   - Launch from your application menu (look for the "R" icon).
   - Or run `rheolwyr` in terminal.

2. **Add Snippets**:
   - Allow you to define triggers (e.g., `;sig`) and replacements.

3. **Expansion**:
   - Type your trigger (e.g., `;sig`).
   - Rheolwyr will backspace the trigger and type the replacement.

### Expansion Modes
- **Short Snippets (< 50 chars)**: Rheolwyr simulates typing each character. This is the most robust method for terminals and Wayland.
- **Long Snippets**: Rheolwyr copies the text to the clipboard and simulates `Ctrl+V`.

## Troubleshooting

### "It backspaces but doesn't type anything"
- Ensure you are in the `input` or `uinput` group:
  ```bash
  sudo usermod -aG input $USER
  sudo usermod -aG uinput $USER
  ```
- Log out and log back in.

### "It pastes the wrong thing"
- This can happen with large snippets if the clipboard is slow. Try typing slower or using shorter snippets if possible.

### "Icon is missing"
- Re-install the package:
  ```bash
  sudo apt install ./rheolwyr_*.deb
  ```
