from itertools import islice

import pytest

from solution import parse_settings

SAMPLE = [
    "# app settings",
    "name = Kavya",
    "",
    "theme=dark",
    "   # another comment",
    "url = https://site.org/?page=2",
]


def endless_settings():
    n = 0
    while True:
        if n >= 10_000:
            raise RuntimeError("Read 10,000 lines from an endless stream: your code is not lazy.")
        yield f"key{n} = {n}"
        n += 1


def test_sample():
    assert list(parse_settings(SAMPLE)) == [
        ("name", "Kavya"),
        ("theme", "dark"),
        ("url", "https://site.org/?page=2"),
    ], "Skip blank and comment lines, strip spaces, and split only at the first '='."


def test_value_with_equals():
    assert list(parse_settings(["query = a=1&b=2"])) == [("query", "a=1&b=2")], "Split at the FIRST '=' only: use split('=', 1)."


def test_empty_value():
    assert list(parse_settings(["password ="])) == [("password", "")], "An empty value is allowed: it becomes ''."


def test_indented_comment_and_spaces_only():
    assert list(parse_settings(["    # note", "     ", "\t", "x=1"])) == [("x", "1")], "Strip the line before you test for '#' or blank."


def test_into_dict():
    assert dict(parse_settings(["a = 1", "b = 2"])) == {"a": "1", "b": "2"}, "The pairs should feed straight into dict()."


def test_is_generator():
    result = parse_settings(SAMPLE)
    assert iter(result) is result, "parse_settings must be a generator function (use yield)."


def test_error_has_line_number():
    with pytest.raises(ValueError) as info:
        list(parse_settings(["# top", "", "a = 1", "oops"]))
    assert "4" in str(info.value), "The error must name the line number, counted from 1, including blank and comment lines."


def test_pairs_before_error_still_arrive():
    gen = parse_settings(["a = 1", "broken", "b = 2"])
    assert next(gen) == ("a", "1"), "The first good line is yielded before the bad line is read."
    with pytest.raises(ValueError):
        next(gen)


def test_lazy():
    assert list(islice(parse_settings(endless_settings()), 2)) == [("key0", "0"), ("key1", "1")], "Must be lazy: read one line, yield one pair. Do not read all lines first."
