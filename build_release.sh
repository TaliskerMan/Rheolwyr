#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Rheolwyr Build Helper${NC}"
echo "---------------------"

# Set Maintainer Identity for GPG Signing and Changelog
export DEBFULLNAME="Chuck Talk"
export DEBEMAIL="chuck@nordheim.online"
GPG_KEY="chuck@nordheim.online"

# 1. Check Dependencies
echo -e "\n${GREEN}[1/4] Checking Dependencies...${NC}"
MISSING_DEPS=()
if ! dpkg -s debhelper >/dev/null 2>&1; then MISSING_DEPS+=("debhelper"); fi
if ! dpkg -s dh-python >/dev/null 2>&1; then MISSING_DEPS+=("dh-python"); fi
if ! dpkg -s python3-all >/dev/null 2>&1; then MISSING_DEPS+=("python3-all"); fi
if ! dpkg -s pybuild-plugin-pyproject >/dev/null 2>&1; then MISSING_DEPS+=("pybuild-plugin-pyproject"); fi

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo -e "${RED}Missing dependencies: ${MISSING_DEPS[*]}${NC}"
    echo "Please install missing packages before continuing."
    exit 1
else
    echo "All dependencies installed."
fi

# Clean previous artifacts
rm -rf artifacts
mkdir -p artifacts

# 2. Increment Version & Run Tests
if [ "$1" != "--no-bump" ]; then
    python3 scripts/increment_version.py
fi

# Get new version
NEW_VERSION=$(dpkg-parsechangelog --show-field Version | cut -d- -f1)
echo "Building Rheolwyr version ${NEW_VERSION}..."

python3 -m unittest discover tests

# Generate SBOM
echo "Generating CycloneDX SBOM via Syft..."
mkdir -p Audit
syft dir:. \
    --exclude "./artifacts" \
    --exclude "./debian" \
    --exclude "./build" \
    --exclude "./.pybuild" \
    --exclude "./Audit" \
    --exclude "./*.deb" \
    --exclude "./*.tar.gz" \
    -o cyclonedx-json > Audit/SBOM-Linux.json
cp Audit/SBOM-Linux.json Audit/sbom.json

# 3. Build Debian Package
echo -e "\n${GREEN}[3/4] Building Debian Package (Signed)...${NC}"
# Generate orig.tar.gz in parent directory to prevent dpkg-buildpackage from prompting
tar --exclude=debian --exclude=.git --exclude=artifacts --exclude=Audit --exclude=.pybuild --exclude=build -czf "../rheolwyr_${NEW_VERSION}.orig.tar.gz" .

dpkg-buildpackage --sign-key="${GPG_KEY}"

# Move artifacts to artifacts
mv ../rheolwyr_${NEW_VERSION}* artifacts/ 2>/dev/null || true
echo "Debian package built and moved to artifacts/"

# Create detached GPG signature for DEB packages per L-DEB-Packaging & L-Release
for deb in artifacts/*.deb; do
    if [ -f "$deb" ]; then
        gpg --batch --yes --armor --pinentry-mode loopback --detach-sign --local-user "${GPG_KEY}" "$deb"
        gpg --batch --yes --pinentry-mode loopback --detach-sign --output "${deb}.sig" --local-user "${GPG_KEY}" "$deb"
    fi
done

# Export public keys
gpg --batch --yes --armor --export "${GPG_KEY}" > artifacts/pubkey.asc
cp artifacts/pubkey.asc artifacts/chuck_pubkey.asc

# Generate single-file and multi-file checksums
for deb in artifacts/*.deb; do
    if [ -f "$deb" ]; then
        sha512sum "$deb" > "${deb}.sha512"
        sha256sum "$deb" > "${deb}.sha256"
    fi
done

cd artifacts
sha512sum * > SHA512SUMS
sha256sum * > SHA256SUMS
cd ..

# 4. Copy to NOBuilds directory
echo -e "\n${GREEN}[4/4] Copying to NOBuilds directory...${NC}"
BUILD_DATE=$(date +%m-%d-%Y)
NOBUILDS_DIR="${HOME}/NOBuilds/Rheolwyr-${BUILD_DATE}-${NEW_VERSION}"
mkdir -p "${NOBUILDS_DIR}"

cp artifacts/* "${NOBUILDS_DIR}/" || true
cp LICENSE "${NOBUILDS_DIR}/" || true
cp README.md "${NOBUILDS_DIR}/" || true
cp Audit/SBOM-Linux.json "${NOBUILDS_DIR}/" || true
cp Audit/sbom.json "${NOBUILDS_DIR}/" || true
if [ -f "Audit/security_report.md" ]; then
    cp Audit/security_report.md "${NOBUILDS_DIR}/"
fi
if [ -f "docs/Rheolwyr_User_Guide.pdf" ]; then
    cp docs/Rheolwyr_User_Guide.pdf "${NOBUILDS_DIR}/"
    cp docs/Rheolwyr_User_Guide.pdf artifacts/
fi

# Generate source code archive
echo "Generating source tarball..."
tar --exclude=debian --exclude=.git --exclude=artifacts --exclude=Audit --exclude=.pybuild --exclude=build -czf "${NOBUILDS_DIR}/rheolwyr_source.tar.gz" .
cp "${NOBUILDS_DIR}/rheolwyr_source.tar.gz" artifacts/

# Refresh multi-file checksums in NOBuilds and artifacts
(
    cd "${NOBUILDS_DIR}"
    sha512sum * > SHA512SUMS 2>/dev/null || true
    sha256sum * > SHA256SUMS 2>/dev/null || true
)
(
    cd artifacts
    sha512sum * > SHA512SUMS 2>/dev/null || true
    sha256sum * > SHA256SUMS 2>/dev/null || true
)

echo -e "${GREEN}SUCCESS!${NC}"
ARTIFACT_PATH=$(realpath artifacts)
echo " - Artifacts are in: $ARTIFACT_PATH"
echo " - Checksum file: $ARTIFACT_PATH/SHA512SUMS"
echo " - Local NOBuilds: ${NOBUILDS_DIR}"
