import typing

from solution import average, best, parse_scores, report


def test_parse_gives_ints():
    got = parse_scores(["ann: 7", "bo:10"])
    assert got == {"ann": 7, "bo": 10}, (
        f"Got {got!r}. Scores must be ints: store int(raw), not raw.strip(). mypy's first error "
        "('got dict[str, str]') points exactly here."
    )


def test_parse_skips_lines_without_colon():
    assert parse_scores(["no colon here", "", "cy: 3"]) == {"cy": 3}, "Lines without ':' (including empty ones) are skipped."


def test_parse_strips_spaces():
    assert parse_scores(["  dee :  12  "]) == {"dee": 12}, "Strip the name; int() accepts spaces around the number."


def test_best_compares_numbers():
    assert best({"a": 9, "b": 10}) == "b", "10 > 9. With string scores '9' > '10', which is why the starter picks 'a'."
    assert best(parse_scores(["a: 9", "b: 10"])) == "b", "parse_scores + best must pick b (10) over a (9)."


def test_best_of_nothing_is_none():
    assert best({}) is None, "best({}) returns None, as the docstring says."


def test_average():
    assert average({"a": 7, "b": 10}) == 8.5, "The average of 7 and 10 is 8.5."
    assert average({}) == 0.0, "average({}) stays 0.0."


def test_report():
    assert report(["ann: 7", "bo: 10"]) == "best: BO, average: 8.5", "Keep the report format: 'best: NAME, average: X.X'."


def test_report_without_scores():
    try:
        got = report(["nothing to see"])
    except AttributeError:
        raise AssertionError(
            "report crashed with AttributeError: best returned None and report called .upper() on it. "
            "This is mypy's 'Item None of str | None has no attribute upper': check `if top is None` first."
        ) from None
    assert got == "no scores", f"With no scores report returns 'no scores', got {got!r}."
    assert report([]) == "no scores", "An empty list of lines also gives 'no scores'."


def test_annotations_tell_the_truth():
    hints = typing.get_type_hints(best)
    ret = hints.get("return")
    assert set(typing.get_args(ret)) == {str, type(None)}, (
        f"best's return annotation is {ret!r}. It can return None, so annotate it as `str | None` "
        "(or Optional[str]), not plain str."
    )
    assert typing.get_type_hints(parse_scores).get("return") == dict[str, int], "parse_scores must stay annotated -> dict[str, int]."
    assert typing.get_type_hints(report).get("return") is str, "report must stay annotated -> str."
    assert typing.get_type_hints(parse_scores).get("lines") == list[str], "Keep the parameter annotation lines: list[str]."
