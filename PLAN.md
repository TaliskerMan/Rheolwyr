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
