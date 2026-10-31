import re
import types

import pytest

from solution import Tokenizer


def test_pattern_compiled_once_with_named_groups():
    t = Tokenizer()
    assert isinstance(t.pattern, re.Pattern), "Compile the master pattern in __init__ and store it in self.pattern."
    names = set(t.pattern.groupindex)
    assert {"NUMBER", "NAME", "OP", "SKIP", "MISMATCH"} <= names, f"The master pattern needs the named groups NUMBER, NAME, OP, SKIP, MISMATCH; found {sorted(names)}."


def test_tokens_is_generator():
    t = Tokenizer()
    assert isinstance(t.tokens("x"), types.GeneratorType), "tokens() should be a generator function (use yield), not build and return a list."


def test_example():
    t = Tokenizer()
    assert list(t.tokens("x = 3.5 + y2")) == [("NAME", "x"), ("OP", "="), ("NUMBER", "3.5"), ("OP", "+"), ("NAME", "y2")], "Use m.lastgroup for the kind and m.group() for the value; skip SKIP tokens."


def test_number_forms():
    t = Tokenizer()
    assert list(t.tokens("7 42 3.25")) == [("NUMBER", "7"), ("NUMBER", "42"), ("NUMBER", "3.25")], "NUMBER is \\d+ with an optional (?:\\.\\d+) part. Did you escape the dot?"


def test_number_then_name():
    t = Tokenizer()
    assert list(t.tokens("12abc")) == [("NUMBER", "12"), ("NAME", "abc")], "'12abc' is a NUMBER then a NAME: a NAME cannot start with a digit."


def test_names_with_underscore_and_digits():
    t = Tokenizer()
    assert list(t.tokens("_tmp x_1")) == [("NAME", "_tmp"), ("NAME", "x_1")], "NAME is a letter or _ followed by letters, digits or _."


def test_all_operators_and_whitespace_kinds():
    t = Tokenizer()
    got = list(t.tokens("(a+b)*c\t-\nd/e"))
    want = [("OP", "("), ("NAME", "a"), ("OP", "+"), ("NAME", "b"), ("OP", ")"), ("OP", "*"),
            ("NAME", "c"), ("OP", "-"), ("NAME", "d"), ("OP", "/"), ("NAME", "e")]
    assert got == want, "OP is one of + - * / = ( ). Tabs and newlines are whitespace too: SKIP should be \\s+. Inside [...] put '-' first or last so it is not a range."


def test_empty_and_blank():
    t = Tokenizer()
    assert list(t.tokens("")) == [], "Empty text gives no tokens."
    assert list(t.tokens("   \n ")) == [], "Only whitespace gives no tokens: SKIP is never yielded."


def test_mismatch_raises_with_position():
    t = Tokenizer()
    with pytest.raises(ValueError) as info:
        list(t.tokens("3 $ 4"))
    msg = str(info.value)
    assert "'$'" in msg or "$" in msg, "The error message should show the bad character."
    assert "2" in msg, "The error message should give the index of the bad character (m.start() is 2 here)."


def test_tokens_before_error_are_yielded():
    t = Tokenizer()
    gen = t.tokens("a + ? b")
    assert next(gen) == ("NAME", "a"), "A generator yields tokens one by one: the first token comes out before the bad character is reached."
    assert next(gen) == ("OP", "+"), "Second token is the '+'."
    with pytest.raises(ValueError):
        next(gen)


def test_reuse_same_tokenizer():
    t = Tokenizer()
    first = list(t.tokens("a"))
    second = list(t.tokens("b = 1"))
    assert first == [("NAME", "a")] and second == [("NAME", "b"), ("OP", "="), ("NUMBER", "1")], "One Tokenizer must work for many texts: keep no state from the previous call."
