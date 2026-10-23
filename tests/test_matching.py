# Copyright (C) 2026 Chuck Talk <chuck@nordheim.online>
# This file is part of Rheolwyr.
#
# Tests for the expansion-critical pure logic: trigger matching (so a trigger
# only fires as a standalone word) and the shift/caps key-mapping table (which
# is exactly the kind of thing that silently regresses).
#
# The trigger tests type text ONE KEY AT A TIME, the way the listener sees it.
# Checking only a finished string (e.g. find_trigger("address")) once let a bug
# through where 'addr' fired while "address" was still being typed.

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from rheolwyr.matching import (  # noqa: E402
    apply_shift_caps,
    find_expansion,
    find_trigger,
    is_word_trigger,
    trailing_token,
)

TRIGGERS = {
    "addr": "123 Main St",
    ";sig": "Best,\nChuck",
    "brb": "be right back",
    "teh": "the",
    ";s": "Short",
}

TAB = "\t"
ENTER = "\n"


def type_text(text, triggers=TRIGGERS):
    """
    Simulate typing *text* key by key through the listener's buffer rules and
    return the text that ends up on screen.

    Mirrors SnippetListener.on_press/_try_expand/expand_snippet: printable keys
    and Space extend the buffer and are checked; Tab and Enter reset it; an
    expansion erases trigger+completer and types snippet+completer.
    """
    screen = ""
    buffer = ""
    for ch in text:
        screen += ch
        if ch in (TAB, ENTER):
            buffer = ""
            continue
        buffer += ch
        match = find_expansion(buffer, triggers)
        if match:
            trigger, completer = match
            screen = screen[: len(screen) - len(trigger) - len(completer)]
            screen += triggers[trigger] + completer
            buffer = completer
    return screen


class TestWordTriggers(unittest.TestCase):
    def test_whole_word_followed_by_space_expands(self):
        assert type_text("addr ") == "123 Main St "
        assert type_text("send to addr now") == "send to 123 Main St now"

    def test_never_fires_inside_a_longer_word(self):
        # The original bug: 'addr' fired while typing "address".
        assert type_text("address ") == "address "
        assert type_text("I will send the address") == "I will send the address"
        assert type_text("tehran ") == "tehran "
        assert type_text("brbx ") == "brbx "

    def test_never_fires_at_the_end_of_a_longer_word(self):
        assert type_text("readdr ") == "readdr "
        assert type_text("xbrb ") == "xbrb "

    def test_waits_for_space(self):
        # Typed but not yet completed: nothing happens.
        assert type_text("addr") == "addr"

    def test_tab_does_not_complete_a_word_trigger(self):
        # Tab can move focus to another field, so it must never cause erasing.
        assert type_text("addr" + TAB) == "addr" + TAB

    def test_punctuation_before_counts_as_word_start(self):
        assert type_text("(addr ") == "(123 Main St "

    def test_find_expansion_reports_the_space(self):
        assert find_expansion("addr ", TRIGGERS) == ("addr", " ")
        assert find_expansion("addr", TRIGGERS) is None


class TestSymbolTriggers(unittest.TestCase):
    def test_expand_instantly(self):
        assert type_text(";sig") == "Best,\nChuck"
        assert find_expansion(";sig", {";sig": "x"}) == (";sig", "")

    def test_expand_anywhere(self):
        assert type_text("hello ;sig") == "hello Best,\nChuck"
        assert type_text("type;sig") == "typeBest,\nChuck"

    def test_longest_trigger_wins_when_both_complete(self):
        assert find_trigger("hello ;sig", TRIGGERS) == ";sig"

    def test_longer_overlapping_trigger_can_be_typed(self):
        # The second bug the key-by-key tests found: with ';s' and ';sig',
        # ';s' used to fire before 'ig' could be typed, so ';sig' never worked.
        assert type_text(";sig") == "Best,\nChuck"

    def test_shorter_overlapping_trigger_fires_on_the_next_key(self):
        assert type_text(";s ") == "Short "
        assert type_text(";sx") == "Shortx"
        # Got partway into ';sig' and then left it: the short one still fires
        # and the extra keys are kept.
        assert type_text(";six") == "Shortix"

    def test_shorter_overlapping_trigger_then_another_trigger(self):
        assert type_text(";s;sig") == "ShortBest,\nChuck"

    def test_unambiguous_symbol_trigger_is_instant(self):
        # ';x' is nobody's prefix, so it fires on its last key.
        assert type_text(";x", {";x": "X", ";sig": "S"}) == "X"

    def test_is_word_trigger(self):
        assert is_word_trigger("addr")
        assert is_word_trigger("2fa")
        assert not is_word_trigger(";sig")
        assert not is_word_trigger("")


class TestBufferHelpers(unittest.TestCase):
    def test_unknown_or_empty(self):
        assert find_trigger("xyz ", TRIGGERS) is None
        assert find_trigger("", TRIGGERS) is None
        assert find_trigger("addr ", {}) is None

    def test_trailing_token_extraction(self):
        assert trailing_token("one two three") == "three"
        assert trailing_token("word\tafter tab") == "tab"
        assert trailing_token("nodelim") == "nodelim"
        assert trailing_token("trailing ") == ""


class TestShiftCaps(unittest.TestCase):
    def test_letters_shift_xor_caps(self):
        assert apply_shift_caps("a", shift=False, caps=False) == "a"
        assert apply_shift_caps("a", shift=True, caps=False) == "A"
        assert apply_shift_caps("a", shift=False, caps=True) == "A"
        # shift + caps cancel out
        assert apply_shift_caps("a", shift=True, caps=True) == "a"

    def test_number_row_symbols_need_shift(self):
        assert apply_shift_caps("1", shift=True, caps=False) == "!"
        assert apply_shift_caps("4", shift=True, caps=False) == "$"
        # caps lock does not affect punctuation/numbers
        assert apply_shift_caps("1", shift=False, caps=True) == "1"

    def test_punctuation_symbols(self):
        assert apply_shift_caps("-", shift=True, caps=False) == "_"
        assert apply_shift_caps("/", shift=True, caps=False) == "?"
        assert apply_shift_caps(";", shift=True, caps=False) == ":"
        assert apply_shift_caps(".", shift=False, caps=False) == "."
