from typing import get_type_hints

from solution import best_per_student, group_scores, students_above

PAIRS = [("asha", 70), ("ravi", 60), ("asha", 90)]
GROUPS = {"asha": [70, 90], "ravi": [60]}


def test_hints():
    assert get_type_hints(group_scores) == {
        "pairs": list[tuple[str, int]],
        "return": dict[str, list[int]],
    }, (
        "group_scores takes list[tuple[str, int]] and returns dict[str, list[int]]."
    )
    assert get_type_hints(best_per_student) == {
        "groups": dict[str, list[int]],
        "return": dict[str, int],
    }, "best_per_student returns one int per student: dict[str, int]."
    assert get_type_hints(students_above) == {
        "groups": dict[str, list[int]],
        "limit": float,
        "return": list[str],
    }, "students_above takes the groups and a float limit, and returns list[str]."


def test_group_scores():
    assert group_scores(PAIRS) == GROUPS, "Collect each student's scores in order of appearance."
    assert group_scores([]) == {}, "No pairs gives an empty dict."


def test_group_scores_keeps_order():
    assert group_scores([("a", 3), ("a", 1), ("a", 2)]) == {"a": [3, 1, 2]}, (
        "Do not sort or deduplicate the scores; keep them as they arrived."
    )


def test_best_per_student():
    assert best_per_student(GROUPS) == {"asha": 90, "ravi": 60}, "Take the max of each list."


def test_students_above():
    assert students_above(GROUPS, 70) == ["asha"], "asha averages 80, ravi averages 60."
    assert students_above(GROUPS, 50) == ["asha", "ravi"], "Both are above 50, sorted by name."


def test_students_above_is_strict():
    assert students_above(GROUPS, 60) == ["asha"], (
        "ravi averages exactly 60, which is not strictly above 60. Use > not >=."
    )
    assert students_above({"zed": [90], "amy": [90]}, 10) == ["amy", "zed"], "Sort the names."
