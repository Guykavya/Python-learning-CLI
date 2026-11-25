import numpy as np
import pandas as pd
import pytest

from solution import key_report


def test_the_statement_example():
    got = key_report(["P05", "p05", "P06 ", "P07", "P07", "105", 105, None])
    assert got == {"duplicates": ["105", "P05", "P07"], "with_spaces": ["P06 "], "case_variants": ["P05"], "numbers_as_text": ["105"]}, f"got {got}"


def test_clean_keys():
    got = key_report(["P01", "P02", "P03", 7, 8.5])
    assert got == {"duplicates": [], "with_spaces": [], "case_variants": [], "numbers_as_text": []}, f"clean keys give four empty lists; got {got}"


def test_spaces_are_ignored_for_duplicates_but_reported():
    got = key_report([" P01", "P01 ", "P02"])
    assert got["duplicates"] == ["P01"] and got["with_spaces"] == [" P01", "P01 "], f"' P01' and 'P01 ' are the same key; both have spaces. Got {got}"
    assert got["case_variants"] == [], "same case: no case variant."


def test_none_and_empty_text_are_ignored():
    got = key_report([None, "", "  ", None, "A"])
    assert got["duplicates"] == [] and got["with_spaces"] == [], "blank keys (None, empty or spaces only) are not keys: they are ignored everywhere."
    assert key_report([None, None])["duplicates"] == [], "None is not a duplicate of None."


def test_numbers_as_text():
    got = key_report(["12", " 7 ", "7a", 12, "007"])
    assert got["numbers_as_text"] == [" 7 ", "007", "12"], f"digit-only strings (after stripping); real numbers are not listed; got {got['numbers_as_text']}"
    assert got["duplicates"] == ["12"], "'12' (text) and 12 (number) are the same key after normalising."
