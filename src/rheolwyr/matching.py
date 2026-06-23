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

    This is the "word" immediately before the cursor — the only candidate that
    may match a trigger, so a trigger fires only as a standalone word.
    """
    token = buffer
    for delim in WORD_DELIMITERS:
        token = token.rsplit(delim, 1)[-1]
    return token


def find_trigger(buffer, triggers):
    """
    Return the trigger that the end of *buffer* matches, or None.

    A match requires the trailing token to equal a registered trigger exactly,
    which prevents a trigger like ``addr`` firing while typing ``address``.
    *triggers* may be any container supporting ``in`` (e.g. a dict of
    trigger -> content).
    """
    token = trailing_token(buffer)
    if token and token in triggers:
        return token
    return None


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
