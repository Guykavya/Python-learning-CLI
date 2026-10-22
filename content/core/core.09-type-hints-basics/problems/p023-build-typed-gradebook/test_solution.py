from typing import get_type_hints

from solution import average, best_student, load, parse_line, ranking, report

BOOK = dict[str, list[int]]
LINES = ["asha, 70", "ravi, 60", "bad line", "asha, 90", "ravi,65", "zed, 101", "", "mia, 80"]


def test_hints():
    assert get_type_hints(parse_line) == {"line": str, "return": tuple[str, int] | None}, (
        "parse_line returns a (name, score) pair or None: -> tuple[str, int] | None."
    )
    assert get_type_hints(load) == {"lines": list[str], "return": BOOK}, (
        "load(lines: list[str]) -> dict[str, list[int]]."
    )
    assert get_type_hints(average) == {"scores": list[int], "return": float}, (
        "average(scores: list[int]) -> float."
    )
    assert get_type_hints(best_student) == {"book": BOOK, "return": str | None}, (
        "best_student returns None for an empty book: -> str | None."
    )
    assert get_type_hints(ranking) == {"book": BOOK, "return": list[tuple[str, float]]}, (
        "ranking returns a list of (name, average) pairs: -> list[tuple[str, float]]."
    )
    assert get_type_hints(report) == {"book": BOOK, "return": list[str]}, (
        "report returns a list of text lines: -> list[str]."
    )


def test_parse_line_good():
    assert parse_line("asha, 70") == ("asha", 70), "Strip the name, convert the score to an int."
    assert parse_line("  ravi ,65") == ("ravi", 65), "Spaces around the name and no space after the comma."
    assert parse_line("zero, 0") == ("zero", 0) and parse_line("full, 100") == ("full", 100), (
        "0 and 100 are valid scores."
    )


def test_parse_line_bad():
    assert parse_line("bad line") is None, "No comma: bad line, return None."
    assert parse_line("a,1,2") is None, "Three parts: bad line."
    assert parse_line(", 5") is None, "An empty name is bad."
    assert parse_line("asha, x") is None, "A score that is not a whole number is bad."
    assert parse_line("asha, 4.5") is None, "A decimal score is bad."
    assert parse_line("asha, 101") is None and parse_line("asha, -1") is None, "Scores must be 0 to 100."
    assert parse_line("") is None, "The empty line is bad."


def test_load():
    assert load(LINES) == {"asha": [70, 90], "ravi": [60, 65], "mia": [80]}, (
        "Skip bad lines and collect each student's scores in order."
    )
    assert load([]) == {}, "No lines, empty book."
    assert load(["bad"]) == {}, "Only bad lines, empty book."


def test_average():
    assert average([70, 90]) == 80.0, "The mean of 70 and 90 is 80.0."
    assert average([]) == 0.0, "An empty list averages to 0.0, not a ZeroDivisionError."
    assert average([60, 65]) == 62.5, "The mean of 60 and 65 is 62.5."


def test_best_student_and_tie():
    book = load(LINES)
    assert best_student(book) == "asha", "asha and mia both average 80.0; the tie goes to the first name alphabetically."
    assert best_student({"zed": [90], "amy": [80], "bo": [90]}) == "bo", "bo and zed tie at 90; bo comes first."
    assert best_student({}) is None, "An empty book has no best student: None."


def test_ranking():
    book = load(LINES)
    assert ranking(book) == [("asha", 80.0), ("mia", 80.0), ("ravi", 62.5)], (
        "Highest average first, ties by name: sort with key (-average, name)."
    )
    assert ranking({}) == [], "An empty book has an empty ranking."


def test_report():
    book = load(LINES)
    assert report(book) == ["asha: 80.0", "mia: 80.0", "ravi: 62.5"], (
        "One line per student in ranking order, average with exactly one decimal."
    )
    assert report({"x": [60]}) == ["x: 60.0"], "60 must print as 60.0, with one decimal."
