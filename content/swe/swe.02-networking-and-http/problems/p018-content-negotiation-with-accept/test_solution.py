import pytest

from solution import choose

JSON_HTML = ["application/json", "text/html"]


def test_examples():
    assert choose("text/html, application/json;q=0.5", JSON_HTML) == "text/html"
    assert choose("*/*", JSON_HTML) == "application/json", "A tie: the server's order decides."
    assert choose("text/*;q=0.8, text/html;q=0", ["text/html", "text/plain"]) == "text/plain"
    assert choose("image/png", ["application/json"]) is None


def test_q_values_decide():
    assert choose("application/json;q=0.3, text/html;q=0.9", JSON_HTML) == "text/html"
    assert choose("application/json;q=0.9, text/html;q=0.3", JSON_HTML) == "application/json"


def test_default_q_is_one():
    assert choose("text/html, application/json;q=0.99", JSON_HTML) == "text/html"


def test_most_specific_range_wins_even_with_a_lower_q():
    assert choose("*/*;q=1.0, application/json;q=0.1, text/html;q=0.2", JSON_HTML) == "text/html", (
        "Exact ranges give the q of an offered type, even when '*/*' has a higher q.")
    assert choose("text/*;q=0.9, text/html;q=0.1, text/plain;q=0.2", ["text/html", "text/plain"]) == "text/plain"


def test_q_zero_means_not_acceptable():
    assert choose("*/*, application/json;q=0", JSON_HTML) == "text/html", "q=0 removes that type, even with */* around."
    assert choose("application/json;q=0", ["application/json"]) is None
    assert choose("text/*;q=0", ["text/html"]) is None


def test_wildcards():
    assert choose("text/*", ["application/json", "text/csv"]) == "text/csv"
    assert choose("application/*;q=0.2, text/*;q=0.4", ["application/json", "text/csv"]) == "text/csv"


def test_parameters_and_case_are_ignored():
    assert choose("TEXT/HTML; charset=utf-8; q=0.8, Application/JSON;level=1", JSON_HTML) == "application/json"
    assert choose("text/html;q=0.5;charset=utf-8", ["text/html"]) == "text/html"


def test_no_or_empty_header_accepts_anything():
    assert choose(None, JSON_HTML) == "application/json"
    assert choose("", JSON_HTML) == "application/json"
    assert choose("   ", JSON_HTML) == "application/json"


def test_nothing_offered():
    assert choose("*/*", []) is None


def test_bad_q_and_junk_ranges():
    assert choose("text/html;q=abc, application/json;q=0.2", JSON_HTML) == "application/json", "A q that is not a number counts as 0."
    assert choose("garbage, text/html", JSON_HTML) == "text/html", "A range with no '/' is ignored."


def test_returns_the_offered_string_as_given():
    assert choose("text/html", ["Text/HTML"]) == "Text/HTML"
