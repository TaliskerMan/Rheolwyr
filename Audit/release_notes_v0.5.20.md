# Rheolwyr v0.5.20 Official Linux Release

Rheolwyr ("Manager" in Welsh, pronounced "Hre-aw-lur") is a Linux-native text snippet and trigger expansion tool designed for Pop!_OS COSMIC and GNOME desktops on Wayland and X11.

## What's Changed in v0.5.20
- **Documentation & Guide Synchronization:** Aligned the official user guide documentation (`Rheolwyr_User_Guide.md` and `Rheolwyr_User_Guide.pdf`) with v0.5.20 release targets and packaging instructions.
- **Dependency Cleanup:** Removed deprecated `pyclip` reference from `requirements.txt` as Wayland/X11 clipboard management is natively integrated with PyGObject/Gtk4.
- **Test Discovery Modernization:** Upgraded test discovery to inherit from `unittest.TestCase`, allowing clean, native execution via `python3 -m unittest discover tests` with 100% test pass rate (20/20).
- **Hardened Debian Packaging Pipeline:** Packaged official Debian distribution (`rheolwyr_0.5.20-1_all.deb`) with GPG detached signing using Chuck Talk's maintainer key (`chuck@nordheim.online`), Syft CycloneDX SBOM generation, and multi-file SHA-512/SHA-256 integrity manifests.

## Package Integrity & Verification

| Asset | Description |
|---|---|
| `rheolwyr_0.5.20-1_all.deb` | Debian/Ubuntu architecture-independent package |
| `rheolwyr_0.5.20-1_all.deb.asc` | GPG ASCII-armored detached signature |
| `rheolwyr_0.5.20-1_all.deb.sig` | GPG binary detached signature |
| `rheolwyr_0.5.20-1_all.deb.sha512` | SHA-512 checksum |
| `rheolwyr_0.5.20-1_all.deb.sha256` | SHA-256 checksum |
| `pubkey.asc` / `chuck_pubkey.asc` | Maintainer GPG public key (`chuck@nordheim.online`) |
| `SBOM-Linux.json` / `sbom.json` | CycloneDX SBOM (Software Bill of Materials) |
| `security_report.md` | Security and vulnerability scan report |
| `Rheolwyr_User_Guide.pdf` | Official User Guide & manual |

### Verification Instructions

Import the release signing key and verify the Debian package:
```bash
# Import Chuck Talk's release signing key
gpg --import chuck_pubkey.asc

# Verify the GPG detached signature
gpg --verify rheolwyr_0.5.20-1_all.deb.asc rheolwyr_0.5.20-1_all.deb

# Verify SHA-512 checksum
sha512sum -c rheolwyr_0.5.20-1_all.deb.sha512
```

### Installation
```bash
sudo apt install ./rheolwyr_0.5.20-1_all.deb
```
