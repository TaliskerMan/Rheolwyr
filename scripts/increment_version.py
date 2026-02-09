#!/usr/bin/env python3
import re
import sys
import subprocess
from datetime import datetime

def get_current_version():
    with open("pyproject.toml", "r") as f:
        content = f.read()
        match = re.search(r'version\s*=\s*"(\d+\.\d+\.\d+)"', content)
        if match:
            return match.group(1)
    return None

def increment_patch_version(version):
    major, minor, patch = map(int, version.split('.'))
    return f"{major}.{minor}.{patch + 1}"

def update_pyproject(new_version):
    with open("pyproject.toml", "r") as f:
        content = f.read()
    
    new_content = re.sub(r'version\s*=\s*"\d+\.\d+\.\d+"', f'version = "{new_version}"', content)
    
    with open("pyproject.toml", "w") as f:
        f.write(new_content)
    print(f"Updated pyproject.toml to version {new_version}")

def update_changelog(new_version):
    # Use dch to add a new entry
    subprocess.run(["dch", "-v", f"{new_version}-1", "--distribution", "unstable", f"Release {new_version}: Auto-incremented release with updated icon"], check=True)
    subprocess.run(["dch", "--release", ""], check=True)
    print(f"Updated debian/changelog to version {new_version}-1")

def main():
    current_version = get_current_version()
    if not current_version:
        print("Could not find current version in pyproject.toml")
        sys.exit(1)
        
    print(f"Current version: {current_version}")
    new_version = increment_patch_version(current_version)
    print(f"New version: {new_version}")
    
    update_pyproject(new_version)
    update_changelog(new_version)

if __name__ == "__main__":
    main()
