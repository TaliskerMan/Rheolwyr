# PLAN

## Release 0.5.19: Hybrid trigger matching and code quality remediation
- Align trigger expansion behavior with specification:
  - Hybrid trigger matching: instant expansion for symbol triggers (`;sig`), word-boundary expansion for word triggers (`addr`).
  - Graceful handling of overlapping symbol triggers (e.g. `;s` vs `;sig`).
  - Tab resets match buffer rather than completing triggers to prevent misdirected backspacing across form fields.
  - Granular key-by-key test coverage.
- Code quality & ShadowAgent compliance:
  - Remediate cognitive complexity in trigger matcher.
  - Refactor `build_guide.js` to modern Node.js standards.
  - Ensure SonarQube Quality Gate passes with 0 issues.
  - Comply with CP-AboutPage, CP-SupplyChain, CP-SBOM, CP-ShiftLeftGate, and L-Release.
- Build signed Debian package and stage release artifacts.
- Merge to main, tag `v0.5.19`, and publish to GitHub Releases.

## Release 0.5.20: Official Linux Release Build and Packaging Hardening
- Documentation & user guide alignment:
  - [x] Align user guide version and remove stale pyclip requirement (commit `2dab12a`).
  - [x] Auto-increment version to 0.5.20 across `pyproject.toml`, `README.md`, `docs/guide/Rheolwyr_User_Guide.md`, and `debian/changelog`.
- Test suite & code quality:
  - [x] Modernize test discovery for standard `unittest` (`python3 -m unittest discover tests`, 20/20 tests passing).
  - [x] Run Semgrep SAST scan across `src/`.
- Supply chain & Debian packaging (`~/sarules`):
  - [x] Generate CycloneDX SBOM via Syft (`Audit/SBOM-Linux.json`, `Audit/sbom.json`).
  - [x] Run vulnerability scans via Grype and OSV-Scanner.
  - [x] Build signed Debian package (`rheolwyr_0.5.20-1_all.deb`).
  - [x] Generate GPG detached signature (`.asc` and `.sig`) with Chuck Talk key (`chuck@nordheim.online`).
  - [x] Generate SHA-256 and SHA-512 checksum manifests (`SHA512SUMS`, `SHA256SUMS`).
  - [x] Stage release archive in `/home/freecode/NOBuilds/Rheolwyr-10-23-2026-0.5.20/`.
- GitHub Release:
  - [x] Tag `v0.5.20`, push to GitHub, and create official public release with all verified artifacts.
