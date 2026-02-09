# Rheolwyr Release Guide

Follow these steps to build and release a new version of Rheolwyr.

## Prerequisites
- `git`
- `dpkg-buildpackage` (from `build-essential` or `debhelper`)
- `flatpak-builder` (optional, for Flatpak)

## Building the Package

1. **Update Version**:
   - Edit `pyproject.toml` (`version = "..."`).
   - update `debian/changelog` (use `dch -i` or edit manually).

2. **Run Build Script**:
   ```bash
   ./build_release.sh
   ```
   This will create a `release_artifacts/` directory containing:
   - `rheolwyr_X.Y.Z_all.deb`
   - `rheolwyr.flatpak` (if Flatpak build succeeds)

## Testing

1. **Install Local Package**:
   ```bash
   sudo apt install ./release_artifacts/rheolwyr_*.deb
   ```
2. **Verify**:
   - Launch `rheolwyr`.
   - Test text expansion in a text editor.
   - Verify the icon appears in the application menu.

## Releasing on GitHub

1. **Commit Changes**:
   ```bash
   git add .
   git commit -m "Release vX.Y.Z"
   git push
   ```

2. **Create Release**:
   - Go to GitHub -> Releases -> Draft a new release.
   - Tag: `vX.Y.Z`
   - Upload the `.deb` file from `release_artifacts/`.
