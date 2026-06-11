# Changelog — Rheolwyr

All notable changes to the Rheolwyr project are documented in this file. This project adheres to Semantic Versioning.

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
