import pytest
from solution import make_slug


def test_basic():
    assert make_slug("Functions in Python!") == "functions-in-python"


def test_runs_and_edges():
    assert make_slug("  Hello,   World  ") == "hello-world", (
        "A run of spaces/punctuation becomes ONE separator, and none at the start or end.")
    assert make_slug("--a--b--") == "a-b"


def test_sep_keyword():
    assert make_slug("Top 10 Tips", sep="_") == "top_10_tips"
    assert make_slug("a b c", sep="--") == "a--b--c"


def test_max_length():
    assert make_slug("Functions in Python", max_length=12) == "functions-in"
    assert make_slug("Functions in Python", max_length=10) == "functions", (
        "Cutting at 10 gives 'functions-'. Remove a separator left dangling at the end.")
    assert make_slug("abc", max_length=10) == "abc"
    assert make_slug("a b c", sep="--", max_length=4) == "a--b"
    assert make_slug("a b c", sep="--", max_length=3) == "a", "Strip the whole '--' suffix, not just one '-'."


def test_nothing_left():
    assert make_slug("!!!") == ""
    assert make_slug("") == ""


def test_digits_and_case():
    assert make_slug("Python 3.14 Release") == "python-3-14-release"


def test_text_positional_only():
    with pytest.raises(TypeError):
        make_slug(text="a b")


def test_options_keyword_only():
    with pytest.raises(TypeError):
        make_slug("a b", "_")
