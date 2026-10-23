from typing import get_type_hints

from solution import age_buckets, mean_age, oldest, parse_rows

ROWS = dict[str, int]
LINES = ["asha, 21", "ravi,17", "", "bad", "zed, abc", "mia, 70", "x, 200", ",5", "   "]
GOOD = [("asha", 21), ("ravi", 17), ("mia", 70)]


def test_hints():
    assert get_type_hints(parse_rows) == {
        "lines": list[str],
        "return": tuple[list[tuple[str, int]], list[str]],
    }, "parse_rows returns a fixed pair: tuple[list[tuple[str, int]], list[str]]."
    assert get_type_hints(oldest) == {
        "rows": list[tuple[str, int]],
        "return": tuple[str, int] | None,
    }, "oldest returns a (name, age) row or None: -> tuple[str, int] | None."
    assert get_type_hints(age_buckets) == {
        "rows": list[tuple[str, int]],
        "return": dict[str, list[str]],
    }, "age_buckets returns dict[str, list[str]]."
    assert get_type_hints(mean_age) == {
        "rows": list[tuple[str, int]],
        "return": float | None,
    }, "mean_age returns None when there are no rows: -> float | None."


def test_parse_rows_good_and_bad():
    rows, bad = parse_rows(LINES)
    assert rows == GOOD, "Valid rows, in order, with the name stripped and the age as an int."
    assert bad == ["bad", "zed, abc", "x, 200", ",5"], (
        "Bad lines are kept exactly as given: wrong number of parts, a bad age, an age out of range, an empty name."
    )


def test_blank_lines_are_ignored():
    assert parse_rows(["", "   ", "\t"]) == ([], []), "Blank lines are neither valid nor bad."
    assert parse_rows([]) == ([], []), "No lines: two empty lists."


def test_age_limits():
    rows, bad = parse_rows(["a, 0", "b, 150", "c, -1", "d, 151", "e, 4.5"])
    assert rows == [("a", 0), ("b", 150)], "0 and 150 are valid ages."
    assert bad == ["c, -1", "d, 151", "e, 4.5"], "Below 0, above 150, and decimals are bad."


def test_too_many_parts():
    assert parse_rows(["a,1,2"]) == ([], ["a,1,2"]), "Exactly two parts are required."


def test_oldest():
    assert oldest(GOOD) == ("mia", 70), "mia has the highest age."
    assert oldest([("a", 5), ("b", 5)]) == ("a", 5), "On a tie the first row wins: use > not >=."
    assert oldest([]) is None, "No rows, no oldest: None."


def test_age_buckets():
    assert age_buckets(GOOD) == {"child": [], "teen": ["ravi"], "adult": ["asha"], "senior": ["mia"]}, (
        "Group the names; all four keys always exist, even with empty lists."
    )
    assert age_buckets([]) == {"child": [], "teen": [], "adult": [], "senior": []}, "No rows: four empty lists."


def test_age_bucket_borders():
    rows = [("a", 12), ("b", 13), ("c", 19), ("d", 20), ("e", 64), ("f", 65)]
    assert age_buckets(rows) == {
        "child": ["a"],
        "teen": ["b", "c"],
        "adult": ["d", "e"],
        "senior": ["f"],
    }, "Borders: 12 child, 13 and 19 teen, 20 and 64 adult, 65 senior."


def test_mean_age():
    assert mean_age(GOOD) == 36.0, "(21 + 17 + 70) / 3 is 36.0."
    assert mean_age([]) is None, "No rows: None, not 0.0 and not a ZeroDivisionError."
