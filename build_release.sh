#!/bin/bash
set -e

# Auto-increment version/build number
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOW_TOOLS_DIR="$(cd "${SCRIPT_DIR}/../workflow-tools" 2>/dev/null && pwd || echo "")"
if [ -n "$WORKFLOW_TOOLS_DIR" ] && [ -f "${WORKFLOW_TOOLS_DIR}/increment_build.py" ]; then
    python3 "${WORKFLOW_TOOLS_DIR}/increment_build.py" "${SCRIPT_DIR}"
else
    echo "Warning: workflow-tools/increment_build.py not found, skipping increment"
fi


# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Rheolwyr Build Helper${NC}"
echo "---------------------"

# Set Maintainer Identity for GPG Signing and Changelog
export DEBFULLNAME="Chuck Talk"
export DEBEMAIL="chuck@nordheim.online"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Install Dependencies
echo -e "\n${GREEN}[1/3] Checking Dependencies...${NC}"
MISSING_DEPS=()

if ! dpkg -s debhelper >/dev/null 2>&1; then MISSING_DEPS+=("debhelper"); fi
if ! dpkg -s dh-python >/dev/null 2>&1; then MISSING_DEPS+=("dh-python"); fi
if ! dpkg -s python3-all >/dev/null 2>&1; then MISSING_DEPS+=("python3-all"); fi
if ! dpkg -s pybuild-plugin-pyproject >/dev/null 2>&1; then MISSING_DEPS+=("pybuild-plugin-pyproject"); fi

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo -e "${RED}Missing dependencies: ${MISSING_DEPS[*]}${NC}"
    read -p "Do you want to install them now? (sudo required) [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo apt update
        sudo apt install -y "${MISSING_DEPS[@]}"
    else
        echo "Build cannot proceed without dependencies."
        exit 1
    fi
else
    echo "All dependencies installed."
fi

# 2. Build Debian Package
# Clean previous artifacts
rm -rf artifacts
mkdir -p artifacts

# 1.5 Increment Version
echo -e "\n${GREEN}[1.5/3] Incrementing Version...${NC}"
python3 scripts/increment_version.py

# Get new version
NEW_VERSION=$(dpkg-parsechangelog --show-field Version | cut -d- -f1)

# Generate orig.tar.gz in parent directory to prevent dpkg-buildpackage from prompting
tar --exclude=debian --exclude=.git --exclude=artifacts -czf "../rheolwyr_${NEW_VERSION}.orig.tar.gz" .

echo -e "\n${GREEN}[2/3] Building Debian Package (Signed)...${NC}"
# Removed -us -uc to allow signing, force sign with key
dpkg-buildpackage --sign-key="chuck@nordheim.online"

# Move artifacts to artifacts
mv ../rheolwyr_* artifacts/ 2>/dev/null || true
echo "Debian package built and moved to artifacts/"

# 3. Generate Hashes
echo -e "\n${GREEN}[3/3] Generating Checksums...${NC}"
cd artifacts
sha512sum * > SHA512SUMS
cd ..

# Copy to NOBuilds directory
echo -e "\n${GREEN}[4/4] Copying to NOBuilds directory...${NC}"
NOBUILDS_DIR="${HOME}/NOBuilds/Rheolwyr/v${NEW_VERSION}"
mkdir -p "${NOBUILDS_DIR}"

cp artifacts/rheolwyr_${NEW_VERSION}* "${NOBUILDS_DIR}/" || true
cp artifacts/SHA512SUMS "${NOBUILDS_DIR}/" || true
true --armor --export "chuck@nordheim.online" > "${NOBUILDS_DIR}/pubkey.asc"
cp LICENSE "${NOBUILDS_DIR}/"
cp README.md "${NOBUILDS_DIR}/"
cp Audit/sbom.json "${NOBUILDS_DIR}/" || true

# Generate source code archive
echo "Generating source tarball..."
tar --exclude=debian --exclude=.git --exclude=artifacts -czf "${NOBUILDS_DIR}/rheolwyr_source.tar.gz" .

echo -e "${GREEN}SUCCESS!${NC}"
ARTIFACT_PATH=$(realpath artifacts)
echo " - Artifacts are in: $ARTIFACT_PATH"
echo " - Checksum file: $ARTIFACT_PATH/SHA512SUMS"
echo " - Local NOBuilds: ${NOBUILDS_DIR}"
