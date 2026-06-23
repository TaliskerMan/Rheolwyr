# Copyright (C) 2026 Chuck Talk <chuck@nordheim.online>
# This file is part of Rheolwyr.
#
# Tests for the expansion-critical pure logic: trigger matching (so a trigger
# only fires as a standalone word) and the shift/caps key-mapping table (which
# is exactly the kind of thing that silently regresses).

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from rheolwyr.matching import (  # noqa: E402
    apply_shift_caps,
    find_trigger,
    trailing_token,
)

TRIGGERS = {"addr": "123 Main St", ";sig": "Best,\nChuck", "brb": "be right back"}


class TestTriggerMatching:
    def test_exact_standalone_word_matches(self):
        assert find_trigger("addr", TRIGGERS) == "addr"
        assert find_trigger("hello addr", TRIGGERS) == "addr"

    def test_substring_does_not_fire(self):
        # The classic bug: 'addr' must NOT fire while typing 'address'.
        assert find_trigger("address", TRIGGERS) is None
        assert find_trigger("readdr", TRIGGERS) is None

    def test_unknown_token(self):
        assert find_trigger("xyz", TRIGGERS) is None
        assert find_trigger("", TRIGGERS) is None

    def test_punctuation_sigil_trigger(self):
        assert find_trigger("type ;sig", TRIGGERS) == ";sig"

    def test_trailing_token_extraction(self):
        assert trailing_token("one two three") == "three"
        assert trailing_token("word\tafter tab") == "tab"
        assert trailing_token("nodelim") == "nodelim"
        assert trailing_token("trailing ") == ""


class TestShiftCaps:
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
