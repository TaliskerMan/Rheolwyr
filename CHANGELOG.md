# Changelog — Rheolwyr

All notable changes to the Rheolwyr project are documented in this file. This project adheres to Semantic Versioning.

---

## [0.5.0] - 2026-06-23

### Security
- **Disclosed the input-group capability.** README and `SECURITY.md` now state
  plainly that enabling expansion adds your user to the `input` group, granting
  read access to every keystroke from every application, system-wide and
  permanently. Joining the group is an explicit, informed opt-in (the package
  never does it automatically), and least-privilege alternatives (dedicated
  service user, udev device scoping, X11-only) are documented.
- **Stopped leaking snippet content to logs.** Removed the `DEBUG` prints of
  trigger/content (which landed in the systemd journal); logging now goes
  through the standard `logging` module, is silent by default, and never
  includes snippet bodies.

### Fixed
- **Trigger matching no longer fires mid-word.** Expansion now requires a word
  boundary (space/tab): `addr ` expands, typing `address` does not. The buffer
  resets on Enter/navigation/editing keys so it can no longer desync from the
  real cursor and delete unintended text.
- **Injection no longer feeds back into the listener.** The evdev listener
  ignores our own virtual injector device by name, plus a short suppression
  window during/after injection, so injected characters and the simulated
  Ctrl+V are not read back or re-triggered.
- **`/dev/uinput` exists on first run.** `postinst` now `modprobe`s `uinput` and
  installs `modules-load.d/uinput.conf`, so injection works out of the box on
  distributions that don't auto-load the module.

### Changed
- **Triggers are cached in memory** and refreshed on snippet add/edit/delete/
  import, instead of querying SQLite on every keystroke.
- **Clipboard restore is content-type aware**: a binary clipboard (e.g. an
  image) is no longer decoded or clobbered during long-snippet paste.
- **Licensing normalized to GPLv3** across source headers (the `LICENSE` file
  and `pyproject` were already GPLv3; several headers incorrectly said AGPL),
  and contact normalized to chuck@nordheim.online.
- **Version reconciled to 0.5.0** (README previously said 0.4.11; tree was
  0.4.15) and the README documents the new word-boundary behaviour.
- **Repository cleanup**: removed build/signing artifacts and GPG key-generation
  batch files from version control and ignored them going forward; removed stray
  `patch_*`/`verify_*`/`test_*` dev scripts.
- **Added a pytest suite** for trigger matching and the shift/caps key map.

---

## [0.4.11] - [0.4.15] - 2026-03-23

### Fixed
- **Wayland Dropped Characters:** Fixed dropped character issues on Wayland by explicitly waiting for the physical key release state before executing expansion keystrokes.

---

## [0.4.3] - [0.4.10] - 2026-02-21

### Added
- **Packaging Dependencies:** Added `hicolor-icon-theme` as a package dependency to resolve missing icons.
- **Aesthetic adjustments:** Updated application launcher icons.

---

## [0.4.0] - [0.4.2] - 2026-02-08

### Added
- **Wayland Expansion Support:** Added support for Wayland text expansion via `uinput` nodes integration.
- **Debian compilation structure:** Built native Debian packaging setups and updated application icons to material style.

---

## [0.3.5] - [0.3.6] - 2026-02-02

### Added
- **Theme Persistence:** Added manual theme switcher (System / Light / Dark) in the header bar and persisted settings.
- **Dynamic Version lookup:** About panel retrieves installed version dynamically.

---

## [0.3.3] - [0.3.4] - 2026-02-01

### Added
- **About dialog panel:** Added local "About Rheolwyr" dialog showing credits and license info.
- **Icon updates:** Corrected package PNG icon files and desktop integration configurations.

---

## [0.3.1] - [0.3.2] - 2026-02-01

### Changed
- **Native Clipboard integrations:** Migrated clipboard handlers from the external `pyclip` library (absent in Debian pools) to native `wl-clipboard` / `xclip` binaries.

---

## [0.3.0] - 2026-02-01

### Changed
- **File System restructurings:** Restructured source files into the unified `rheolwyr` module.
- **XDG Compliance:** Relocated local database cache `snippets.db` into the user's `XDG_DATA_HOME/rheolwyr/` folder.

---

## [0.1.0] - [0.2.0] - 2026-02-01

### Added
- **Initial Release:** Native background text expander utility using `pynput` and `evdev` to intercept triggers and execute keystroke simulation.
