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

# Characters that separate words in the match buffer.
WORD_DELIMITERS = (" ", "\t")

# The key that completes a letter/number ("word") trigger. Only Space: Tab is
# deliberately excluded because in forms and browsers it moves focus to the
# next field, and the backspaces that erase the trigger would then land there.
WORD_TRIGGER_COMPLETER = " "

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


def is_word_trigger(trigger):
    """True if *trigger* starts with a letter or digit (e.g. 'addr', 'brb')."""
    return bool(trigger) and trigger[0].isalnum()


def find_expansion(buffer, triggers):
    """
    Decide whether the end of *buffer* (the text just typed) completes a trigger.

    Returns ``(trigger, completer)`` or None. *completer* is whatever was
    typed after the trigger that completed it: "" for a symbol trigger, " "
    for a word trigger, or the extra keys typed after an overlapping symbol
    trigger (rule 3). The caller erases ``trigger + completer``, types
    ``snippet + completer`` (so those keys are kept), and restarts the buffer
    from ``completer``.

    Rules (hybrid):
    1. Symbol triggers (first character not a letter/digit, e.g. ';sig', '+pp')
       expand the moment they are complete, wherever they are typed.
    2. Word triggers (e.g. 'addr', 'brb') expand only when followed by Space,
       and only as a whole word: the character before them must be the start
       of the buffer or a non-letter/digit. So typing "address" never fires
       'addr', and "readdr " doesn't either.
    3. Overlapping symbol triggers: if a symbol trigger is the start of a
       longer one (';s' and ';sig'), it waits. Typing the longer one expands
       the longer one; typing anything else expands the short one at the first
       key that rules the longer one out, and that key is kept (returned in
       *completer*). Without this, ';sig' could never be typed.
    4. If several triggers complete at once, the longest wins.
    """
    if not buffer or not triggers:
        return None

    names = [t for t in triggers if t]
    candidates = []
    for trigger in names:
        if is_word_trigger(trigger):
            ending = trigger + WORD_TRIGGER_COMPLETER
            if not buffer.endswith(ending):
                continue
            start = len(buffer) - len(ending)
            if start == 0 or not buffer[start - 1].isalnum():
                candidates.append((trigger, WORD_TRIGGER_COMPLETER))
            continue

        # Symbol trigger.
        if buffer.endswith(trigger):
            if not _could_still_become_longer(trigger, names):
                candidates.append((trigger, ""))
            continue  # otherwise wait: a longer trigger may be on its way
        start = buffer.rfind(trigger)
        if start < 0:
            continue
        tail = buffer[start:]
        # Fire only on the key that ended the wait: the text was still a
        # possible longer trigger one key ago, and no longer is.
        if (_could_still_become_longer(tail[:-1], names)
                and not _could_still_become_longer(tail, names)
                and tail not in triggers):
            candidates.append((trigger, tail[len(trigger):]))

    if not candidates:
        return None
    return max(candidates, key=lambda c: len(c[0]))


def _could_still_become_longer(text, names):
    """True if *text* is the start of some longer trigger in *names*."""
    return any(len(n) > len(text) and n.startswith(text) for n in names)


def find_trigger(buffer, triggers):
    """
    Return the trigger completed by the end of *buffer*, or None.

    Thin wrapper around :func:`find_expansion` kept for existing callers.
    """
    match = find_expansion(buffer, triggers)
    return match[0] if match else None


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
