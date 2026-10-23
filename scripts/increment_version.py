#!/usr/bin/env python3
# Copyright (C) 2026 Chuck Talk <cwtalk1@gmail.com>
# This file is part of Rheolwyr.
#
# Rheolwyr is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, version 3.
#
# Rheolwyr is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY. See the GNU AGPL v3 for details.

import os
import re
import subprocess
import sys

PYPROJECT_PATH = "pyproject.toml"


def get_current_version():
    with open(PYPROJECT_PATH, "r") as f:
        content = f.read()
        match = re.search(r'version\s*=\s*"(\d+\.\d+\.\d+)"', content)
        if match:
            return match.group(1)
    return None


def increment_patch_version(version):
    major, minor, patch = map(int, version.split('.'))
    return f"{major}.{minor}.{patch + 1}"


def update_pyproject(new_version):
    with open(PYPROJECT_PATH, "r") as f:
        content = f.read()

    new_content = re.sub(r'version\s*=\s*"\d+\.\d+\.\d+"', f'version = "{new_version}"', content)

    with open(PYPROJECT_PATH, "w") as f:
        f.write(new_content)
    print(f"Updated pyproject.toml to version {new_version}")


def update_readme(new_version):
    readme_path = "README.md"
    if os.path.exists(readme_path):
        with open(readme_path, "r") as f:
            content = f.read()
        new_content = re.sub(r'Version \d+\.\d+\.\d+', f'Version {new_version}', content)
        with open(readme_path, "w") as f:
            f.write(new_content)
        print(f"Updated README.md to version {new_version}")


def update_user_guide(new_version):
    guide_path = "docs/guide/Rheolwyr_User_Guide.md"
    if os.path.exists(guide_path):
        with open(guide_path, "r") as f:
            content = f.read()
        new_content = re.sub(r'version: \d+\.\d+\.\d+.*', f'version: {new_version}', content)
        new_content = re.sub(r'rheolwyr_\d+\.\d+\.\d+-1_all\.deb', f'rheolwyr_{new_version}-1_all.deb', new_content)
        with open(guide_path, "w") as f:
            f.write(new_content)
        print(f"Updated {guide_path} to version {new_version}")


def update_changelog(new_version):
    # Set maintainer identity for dch
    os.environ["DEBFULLNAME"] = "Chuck Talk"
    os.environ["DEBEMAIL"] = "chuck@nordheim.online"
    # Use dch to add a new entry
    subprocess.run([
        "dch", "-v", f"{new_version}-1", "--distribution", "unstable",
        f"Release {new_version}: User guide update, pyclip dependency cleanup, and hardened Debian release packaging"
    ], check=True, env=os.environ)
    subprocess.run(["dch", "--release", ""], check=True, env=os.environ)
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
    update_readme(new_version)
    update_user_guide(new_version)
    update_changelog(new_version)


if __name__ == "__main__":
    main()
