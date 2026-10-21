import pytest

from solution import word_frequency


def test_simple_counts():
    assert word_frequency("to be or not to be") == {"to": 2, "be": 2, "or": 1, "not": 1}, (
        "Count every occurrence of each word.")


def test_case_is_ignored():
    assert word_frequency("The the THE") == {"the": 3}, "Lower-case the text before counting."


def test_end_punctuation_is_dropped():
    assert word_frequency("Hi, hi! HI.") == {"hi": 3}, "Strip punctuation from both ends of each word."


def test_inner_punctuation_stays():
    assert word_frequency("don't well-known") == {"don't": 1, "well-known": 1}, (
        "Only the ends are stripped. Punctuation inside a word stays, so do not use replace().")


def test_any_whitespace_separates_words():
    assert word_frequency("a  b\tc\nd   a") == {"a": 2, "b": 1, "c": 1, "d": 1}, (
        "Use text.split() with no argument: it splits on any run of spaces, tabs and new lines.")


def test_only_punctuation_is_not_a_word():
    assert word_frequency("hello -- world") == {"hello": 1, "world": 1}, (
        "A piece that is only punctuation becomes empty after stripping: skip it.")


@pytest.mark.parametrize("text", ["", "   ", "\n\t", "!!! ..."])
def test_no_words_gives_empty_dict(text):
    assert word_frequency(text) == {}, f"{text!r} has no words: the result must be an empty dict."


def test_returns_a_plain_dict():
    result = word_frequency("a")
    assert type(result) is dict, "Return a dict."
