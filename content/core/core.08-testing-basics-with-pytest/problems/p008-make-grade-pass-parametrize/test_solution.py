import pytest

from solution import grade


@pytest.mark.parametrize("marks, expected", [
    (100, "A"), (95, "A"), (90, "A"),
    (89, "B"), (75, "B"),
    (74, "C"), (60, "C"),
    (59, "D"), (40, "D"),
    (39, "F"), (1, "F"), (0, "F"),
])
def test_grade_table(marks, expected):
    assert grade(marks) == expected, (
        f"grade({marks}) should be {expected!r}. Check whether this border value needs >= or >.")


@pytest.mark.parametrize("bad", [-1, 101, 1000, -50])
def test_marks_out_of_range(bad):
    with pytest.raises(ValueError):
        grade(bad)
