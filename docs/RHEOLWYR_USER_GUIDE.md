# Rheolwyr - Comprehensive User Guide

Welcome to **Rheolwyr**! Rheolwyr (Welsh for "Manager," pronounced *Hre-aw-lur*) is a native, high-performance text expander explicitly designed for modern Linux desktops running GNOME or Cosmic on Wayland and X11.

Built with love for the community at large, Rheolwyr was developed with a singular, unwavering philosophy: **Privacy, security, and control matter.**

---

## 🔒 1. Philosophy: Your Words Are Yours

Every modern desktop needs a snippet tool for efficient work execution. However, many contemporary typing assistants and expanders operate in the cloud. They log your keystrokes, upload your thoughts, train machine learning models on your syntax, and gather your unique writing style to package it for others.

**Rheolwyr operates differently:**
* **Zero Telemetry:** Your snippets never leave your local machine.
* **No Cloud Syncing:** Your thoughts and styles are your private property, not data to be shared online.
* **Local Database:** All snippets are stored securely in a local SQLite database entirely within your control.

---

## 🚀 2. What Rheolwyr Does

Rheolwyr saves you thousands of keystrokes by automatically expanding short "triggers" into longer blocks of text.

**What it is used for:**
* **Email Signatures:** Type `;sig` and instantly expand it to your full, multi-line professional signature.
* **Code Blocks:** Create triggers for commonly used programming boilerplate.
* **Support Responses:** Rapidly deploy standardized replies in helpdesk environments.

### Expansion Modes (What You Need to Be Aware Of)
Rheolwyr dynamically chooses how to inject text based on the length of your snippet:
1. **Short Snippets (< 50 characters):** Rheolwyr simulates typing each individual character. This is the most robust method and guarantees compatibility across secure terminal environments and strict Wayland sandboxes.
2. **Long Snippets (50+ characters):** Simulating hundreds of keystrokes takes too long. For large blocks of text, Rheolwyr instantly copies the text to your system clipboard, simulates a `Ctrl+V` paste command, and restores your previous clipboard history.

---

## 💾 3. Installation Instructions

Because Rheolwyr operates at the system level to monitor global keystrokes and inject text across all applications, it must be installed natively via a Debian package (`.deb`). 

### Step 1: Install the Package
Download the latest `rheolwyr_*_all.deb` file from the official releases and run:
```bash
sudo apt install ./rheolwyr_*_all.deb
```
*(Using `apt` instead of `dpkg` automatically resolves any required dependencies like `xclip` and `wl-clipboard`.)*

### Step 2: System Configuration (CRITICAL)
For text expansion to function on Wayland, your user account **must** have permission to monitor input devices and inject keys via `uinput`.
1. Add your user to the required system groups:
   ```bash
   sudo usermod -aG input,uinput $USER
   ```
2. **Log Out & Log In:** Group permission changes will *not* take effect until you completely log out of your desktop session and log back in (or reboot your machine).

---

## 🎮 4. Navigation & Usage

### The Main Interface
1. **Launch the App:** Open your Application grid and launch Rheolwyr (look for the "R" icon).
2. **System Tray:** Rheolwyr is designed to run silently in the background. Closing the main window will minimize it to your system tray or background processes.

### Creating a Snippet
1. Click the **Add (+) button** in the split-view editor.
2. **Trigger:** Define the short keystroke that will activate the snippet. *(Pro-tip: Prefix triggers with a punctuation mark like a semicolon `;` so you don't accidentally expand common words. Example: `;em` instead of `em`)*.
3. **Replacement Text:** Type the full text block you want to appear when the trigger is typed.
4. **Save:** Your snippet is instantly saved to the local database and is immediately active.

### Triggering a Snippet
1. Open any application (a text editor, web browser, or terminal).
2. Type your trigger (e.g., `;sig`).
3. Rheolwyr intercepts the keystrokes, automatically hits `Backspace` to remove your trigger text, and seamlessly injects the replacement text.

---
*Rheolwyr - Your style, your thoughts, your control. Distributed under the GNU GPL v3.*
