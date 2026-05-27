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

print("Checking environment for Rheolwyr...")

# Check text expansion dependencies
try:
    import evdev
    print("[PASS] evdev is installed.")
except ImportError:
    print("[FAIL] evdev is NOT installed. Please run scripts/setup_permissions.sh or install python3-evdev.")

if os.access("/dev/uinput", os.W_OK):
    print("[PASS] /dev/uinput is writable.")
else:
    print("[FAIL] /dev/uinput is NOT writable. You may need to run scripts/setup_permissions.sh and REBOOT or LOGOUT.")

# Check pynput
try:
    from pynput import keyboard
    print("[PASS] pynput is installed.")
except ImportError:
    print("[FAIL] pynput is NOT installed.")

# Check groups
import grp
import os

user = os.environ.get('USER', 'freecode')
try:
    groups = [g.gr_name for g in grp.getgrall() if user in g.gr_mem]
    gid = os.getgid()
    group = grp.getgrgid(gid).gr_name
    groups.append(group)

    print(f"User '{user}' groups: {groups}")

    if 'input' in groups and 'uinput' in groups:
        print("[PASS] User is in 'input' and 'uinput' groups.")
    else:
        print("[FAIL] User is MISSING from 'input' or 'uinput' groups.")
        print("       Run 'sudo usermod -aG input $USER && sudo usermod -aG uinput $USER'")
        print("       Then LOG OUT and LOG BACK IN.")
except Exception as e:
    print(f"Could not check groups: {e}")

print("\nIf all checks passed, Rheolwyr should work with the new evdev injection.")
