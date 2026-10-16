title: Rheolwyr
subtitle: Installation and User Guide
version: 0.5.19 (with the October 2026 fixes)
platforms: Linux (GNOME, COSMIC; Wayland and X11)
## About Rheolwyr

Rheolwyr (Welsh for "manager", pronounced roughly *HRE-aw-loor*) is a text expander for Linux. You type a short trigger, such as `;sig`, and Rheolwyr replaces it with longer text, such as your email signature, in almost any application. It's built for GNOME and Pop!_OS COSMIC, on Wayland or X11.

Rheolwyr is the Linux counterpart of Shine, Nordheim Online's text expander for the Mac.

**What Rheolwyr does**

- Stores your snippets (a name, a trigger and the text) in a local database.
- Watches for triggers as you type and replaces them with your snippet.
- Restores your previous clipboard text after pasting long snippets.
- Backs up and restores snippets as JSON.

Rheolwyr is free, open-source software under the GNU General Public License v3. Source: github.com/TaliskerMan/Rheolwyr.

## Read this first: what Rheolwyr needs to see

> **Important:** To spot your triggers, a text expander must read every key you press. On **Wayland**, Rheolwyr reads the keyboard directly from `/dev/input`, which requires adding your account to the **`input` group**. That membership lets your account read **every keystroke from every application, system-wide and permanently**, not only while Rheolwyr runs, until you remove yourself from the group.

What Rheolwyr does to limit the risk:

- It **never records or logs keystrokes** or snippet text. It keeps only the last 50 characters in memory to match triggers.
- It has **no network code**. Nothing is sent anywhere.
- The package **never adds you to the group automatically**. You choose to.

Least-privilege alternatives, for people who'd rather not make their login account able to read all input:

- **A dedicated service user** in the `input` and `uinput` groups that runs the listener, instead of your own account.
- **A udev rule for just your keyboard**, granting read access to that one device instead of all input devices.
- **An X11 session**, where Rheolwyr uses X11 input and doesn't need the `input` group (X11 has its own security trade-offs).

The repository's `SECURITY.md` explains these options in more detail.

## System requirements

| | |
|---|---|
| Operating system | Debian, Ubuntu, Pop!_OS or a derivative |
| Desktop | GNOME or COSMIC, Wayland or X11 |
| Installed with the package | Python 3, GTK 4 and Libadwaita bindings, `python3-evdev`, `python3-pynput`, `wl-clipboard` or `xclip` |
| Wayland only | Your account in the `input` and `uinput` groups |

## Installing Rheolwyr

1. Download `rheolwyr_<version>_all.deb` from the release page.
2. Install it:

```
sudo apt install ./rheolwyr_0.5.19-1_all.deb
```

   The installer creates a `uinput` group, installs a udev rule so that group can use the virtual keyboard (`/dev/uinput`), loads the `uinput` kernel module now and at every boot, and prints a security notice.

3. **To enable expansion on Wayland**, after reading the section above:

```
sudo usermod -aG input,uinput "$USER"
```

4. **Log out and log back in** (or reboot). Group changes only take effect in a new session.
5. Open **Rheolwyr** from your applications menu.

### From source (development)

```
sudo apt install libcairo2-dev libgirepository1.0-dev pkg-config python3-dev xclip wl-clipboard
pip install -r requirements.txt
python -m rheolwyr.main
```

### Uninstalling

`sudo apt remove rheolwyr`, then remove yourself from the groups you joined:

```
sudo gpasswd -d "$USER" input
sudo gpasswd -d "$USER" uinput
```

Log out and back in. Delete `~/.local/share/rheolwyr/` and `~/.config/rheolwyr/` to remove your snippets and settings.

## Quick start

1. Open Rheolwyr. Your snippets are listed on the left; the editor is on the right.
2. Click **+**.
3. Fill in **Snippet Name** (for example `Signature`), **Trigger Text** (for example `;sig`) and **Snippet Content**.
4. Click **Save**. The snippet works immediately.
5. In any text editor, type `;sig`. Rheolwyr erases the trigger and types your text.

> **Tip:** Rheolwyr expands only while it's running, and closing its window quits it. Minimize the window to keep it working in the background.

## Using Rheolwyr

### Writing good triggers

There are two kinds of trigger:

- **Symbol triggers** start with a symbol, such as `;sig` or `+addr`. They expand as soon as you finish typing them, wherever you type them.
- **Word triggers** start with a letter or number, such as `brb` or `addr`. They expand only when you type them as a whole word and press **Space**; Rheolwyr keeps the space. They never fire inside a longer word, so typing "address" doesn't touch `addr`.

**Tab doesn't complete a trigger.** In forms and browsers Tab moves to another field, where Rheolwyr's backspaces could erase the wrong text, so Tab simply clears what Rheolwyr is matching.

**Overlapping symbol triggers.** If one symbol trigger is the start of another, such as `;s` and `;sig`, Rheolwyr waits. Type `;sig` and you get the `;sig` snippet. Type `;s` followed by anything else, such as a space, and `;s` expands at that key, which is kept. So `;s` expands one key later than a trigger with no overlap.

### How expansion works

1. Rheolwyr erases the trigger with backspaces (plus the Space, for a word trigger).
2. Snippets under 50 characters are **typed** in, using a virtual keyboard on Wayland or X11 input on X11.
3. Longer snippets are **pasted**: Rheolwyr puts the text on the clipboard, presses Ctrl+V, then restores your previous clipboard text. (If your clipboard held an image, it isn't restored.)

Then it re-types any key it erased after the trigger, such as your Space. Rheolwyr ignores its own typing so expansions don't trigger again.

### Editing and deleting

Click a snippet to load it, change it, and click **Save**. To delete it, select it and click the trash button in the editor header. Deleting is immediate, so export a backup first if you might want it back.

### The menu

Click the menu button (☰):

| Item | What it does |
|---|---|
| System / Light / Dark | Appearance; remembered between runs |
| Import Snippets | Adds snippets from a JSON file; skips exact duplicates |
| Export Snippets | Saves all snippets to a JSON file |
| Instructions | A short how-to |
| About Rheolwyr | Version, license and credits |

## Privacy and files

| Item | Location |
|---|---|
| Snippets | `~/.local/share/rheolwyr/snippets.db` |
| Settings | `~/.config/rheolwyr/config.json` |
| udev rule (from the package) | `/lib/udev/rules.d/99-rheolwyr.rules` |
| Module loading (from the package) | `/usr/lib/modules-load.d/uinput.conf` |

Snippets are stored unencrypted. **Don't keep passwords or other secrets in a text expander.**

## Limitations

- **Terminals.** Long snippets are pasted with Ctrl+V, which most Linux terminals don't use for paste, so long snippets may not appear there. Short (typed) snippets work.
- **Clipboard history tools** may record long snippets, because they pass through the clipboard.
- **No password-field detection.** Linux has no equivalent of macOS Secure Input, so Rheolwyr can't tell when you're typing a password. It never stores what you type, but quit it first if you'd rather it not see a password at all.
- **Plain text only**, with no formatting, dates or cursor placement.
- **Keyboard layout.** Typed snippets use a US-style key map on Wayland; unusual characters in short snippets may come out differently on other layouts. Long snippets are pasted and aren't affected.
- **Only while running.** Closing the window stops expansion.

## Troubleshooting

**Nothing expands on Wayland.** Run `groups` and check for `input` and `uinput`. If they're missing, add them (see *Installing*) and log out and back in. Make sure Rheolwyr is open.

**Nothing expands at all.** Check `/dev/uinput` exists (`ls -l /dev/uinput`); if not, run `sudo modprobe uinput`.

**The trigger disappears but nothing appears.** You may be in a terminal with a long snippet; try a text editor.

**A word trigger doesn't expand.** Press **Space** after it; Tab and Enter don't complete triggers.

**A short symbol trigger expands a key late.** It's the start of a longer trigger (for example `;s` and `;sig`), so Rheolwyr waits to see which you mean. Rename one of them if that bothers you.

**Import says 0 snippets.** Every snippet in the file already exists, or the file isn't a Rheolwyr JSON export.

## Support and license

Report problems on GitHub (github.com/TaliskerMan/Rheolwyr) or email **chuck@nordheim.online**. For security issues, see `SECURITY.md`.

| | |
|---|---|
| Website | nordheim.online |
| Source code | github.com/TaliskerMan/Rheolwyr |
| License | GNU GPL v3 (no warranty) |
| Copyright | © 2026 Chuck Talk, Nordheim Online, LLC |
