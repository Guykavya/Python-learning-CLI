import re

import solution
from solution import strong


def test_strong_re_is_compiled():
    assert isinstance(solution.STRONG_RE, re.Pattern), "STRONG_RE must be a compiled pattern: STRONG_RE = re.compile(r'...')."
    assert "(?=" in solution.STRONG_RE.pattern, "Put the rules into ONE pattern with lookaheads (?=...), not into several if-statements."


def test_valid_passwords():
    assert strong("Abcdefg1") is True, "8 characters with an upper, a lower and a digit is strong. Return a bool, not the Match."
    assert strong("1aB?????") is True, "The rules can be met in any order: each lookahead scans with .* from the start."
    assert strong("Xx9!@#$%^&*()long") is True, "Symbols are allowed and long passwords are fine."
    assert strong("Pässwörd1") is True, "Non-English letters are allowed as extra characters; the rules only need one A-Z, one a-z, one 0-9."


def test_too_short():
    assert strong("Abcdef1") is False, "7 characters is too short: the consuming part needs {8,}."
    assert strong("") is False, "The empty password is not strong."


def test_missing_classes():
    assert strong("abcdefg1") is False, "No upper-case letter: add (?=.*[A-Z])."
    assert strong("ABCDEFG1") is False, "No lower-case letter: add (?=.*[a-z])."
    assert strong("Abcdefgh") is False, "No digit: add (?=.*[0-9])."


def test_whitespace_rejected():
    assert strong("Abcd efg1") is False, "A space inside is not allowed: consume with \\S, not '.'."
    assert strong("Abcdefg1\t") is False, "A tab is whitespace too."
    assert strong(" Abcdefg1") is False, "A leading space is not allowed."


def test_trailing_newline_rejected():
    assert strong("Abcdefg1\n") is False, "'$' also matches just before a final newline, so ^...$ accepts 'Abcdefg1\\n'. Use fullmatch (or \\Z)."


def test_lookahead_sees_whole_password():
    assert strong("abcdefgh" + "A1") is True, "The capital and digit are at the very end: lookaheads with .* must scan to the end."
    assert strong("A1" + "b" * 20) is True, "Long passwords: {8,} has no upper limit."
