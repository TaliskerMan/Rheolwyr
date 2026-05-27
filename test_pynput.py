# Copyright (C) 2026 Chuck Talk <cwtalk1@gmail.com>
# This file is part of Rheolwyr.
#
# Rheolwyr is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, version 3.
#
# Rheolwyr is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY. See the GNU AGPL v3 for details.


import time

from pynput import keyboard


def on_press(key):
    print(f"Key pressed: {key}")
    return False # Stop listener

print("Starting listener test...")
try:
    with keyboard.Listener(on_press=on_press) as listener:
        print("Listener started. Waiting for input (simulated or real)...")
        # We can't easily simulate input to ourselves if pynput input injection is also broken/restricted
        # But we can see if it crashes on start
        time.sleep(2)
        print("Listener running ok so far.")
except Exception as e:
    print(f"Listener failed: {e}")
