#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Rheolwyr Build Helper${NC}"
echo "---------------------"

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
if ! command_exists flatpak-builder; then MISSING_DEPS+=("flatpak-builder"); fi

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
rm -rf release_artifacts
mkdir -p release_artifacts

# 1.5 Increment Version
echo -e "\n${GREEN}[1.5/3] Incrementing Version...${NC}"
python3 scripts/increment_version.py

echo -e "\n${GREEN}[2/3] Building Debian Package...${NC}"
dpkg-buildpackage -us -uc

# Move artifacts to release_artifacts
mv ../rheolwyr_* release_artifacts/ 2>/dev/null || true
echo "Debian package built and moved to release_artifacts/"

# 3. Build Flatpak
echo -e "\n${GREEN}[3/3] Building Flatpak...${NC}"
REPO_DIR="repo"
BUILD_DIR="build-dir"

# Install Runtime if missing
# echo "Ensuring GNOME Runtime 46 is installed..."
# flatpak install -y --user org.gnome.Platform/x86_64/46 org.gnome.Sdk/x86_64/46 || true

# Build
flatpak-builder --user --force-clean --repo=$REPO_DIR $BUILD_DIR com.taliskerman.rheolwyr.yml
echo "Flatpak built successfully."

# Bundle
flatpak build-bundle $REPO_DIR release_artifacts/rheolwyr.flatpak com.taliskerman.rheolwyr
echo -e "${GREEN}SUCCESS!${NC}"
echo " - Artifacts are in: release_artifacts/"
