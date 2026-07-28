# Copyright (C) 2026 Chuck Talk <chuck@nordheim.online>
# This file is part of Rheolwyr.
#
# Rheolwyr is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, version 3.
#
# Rheolwyr is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY. See the GNU GPL v3 for details.

"""
Pure, dependency-free helpers for trigger matching and key mapping.

This module deliberately imports nothing from GTK (`gi`) or `evdev`, so the
expansion-critical logic — the part most prone to silent regressions — can be
unit-tested on any platform without the Linux desktop stack.
"""

# Characters that complete a word (and may therefore trigger an expansion).
WORD_DELIMITERS = (" ", "\t")

# Shifted forms of the number row and punctuation keys (US layout).
SHIFT_SYMBOLS = {
    '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
    '6': '^', '7': '&', '8': '*', '9': '(', '0': ')',
    '-': '_', '=': '+', '[': '{', ']': '}',
    ';': ':', "'": '"', '`': '~', '\\': '|',
    ',': '<', '.': '>', '/': '?',
}


def trailing_token(buffer):
    """
    Return the maximal run of non-delimiter characters at the end of *buffer*.

    This helper is preserved for backward compatibility and string boundary checks.
    """
    token = buffer
    for delim in WORD_DELIMITERS:
        token = token.rsplit(delim, 1)[-1]
    return token


def find_trigger(buffer, triggers):
    """
    Return the trigger that the end of *buffer* matches, or None.

    Instant expansion logic (CP-ChangeComments: Updated trigger matching to fire
    immediately upon shortcut entry without requiring Space or Tab delimiters,
    cleanly backspacing all shortcut characters including sigils like ';'):
    1. A trigger matches if buffer ends with the trigger string.
    2. Sigil triggers (starting with non-alphanumeric chars like ';', ':', '!', '+')
       expand instantly whenever completed.
    3. Plain word triggers expand instantly if preceded by a non-alphanumeric character
       (or start of buffer) to prevent false positives while typing longer words (e.g. 'address').
    4. If multiple triggers match, the longest trigger takes precedence (e.g. ';sig' over ';s').
    """
    if not buffer or not triggers:
        return None

    matching_triggers = []
    for trigger in triggers:
        if not trigger:
            continue
        if buffer.endswith(trigger):
            # Check boundary condition for plain word triggers
            first_char = trigger[0]
            if not first_char.isalnum():
                # Sigil trigger (e.g. ';sig', '+pp') -> instant match
                matching_triggers.append(trigger)
            else:
                # Alphanumeric trigger (e.g. 'brb', 'addr') -> check preceding character
                prefix_len = len(buffer) - len(trigger)
                if prefix_len == 0 or not buffer[prefix_len - 1].isalnum():
                    matching_triggers.append(trigger)

    if not matching_triggers:
        return None

    # Return the longest matching trigger to resolve overlaps (e.g. ';sig' over ';s')
    return max(matching_triggers, key=len)


def apply_shift_caps(base_char, shift, caps):
    """
    Apply shift/caps-lock to a base character to get the produced character.

    Letters honour the XOR of shift and caps; other keys use the shifted symbol
    table only when shift is held (caps lock does not affect punctuation).
    """
    if base_char.isalpha():
        return base_char.upper() if (shift != caps) else base_char.lower()
    if shift:
        return SHIFT_SYMBOLS.get(base_char, base_char)
    return base_char
