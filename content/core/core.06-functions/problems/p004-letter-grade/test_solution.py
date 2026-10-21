import pytest
from solution import letter_grade


@pytest.mark.parametrize("score, grade", [(95, "A"), (100, "A"), (90, "A"), (89.5, "B"), (75, "B"),
                                          (74, "C"), (60, "C"), (59.99, "D"), (40, "D"), (39.9, "F"), (0, "F")])
def test_grades(score, grade):
    assert letter_grade(score) == grade, (
        f"letter_grade({score}) should be {grade!r}. Check the boundaries use >= and that you test "
        "from the highest grade down.")


@pytest.mark.parametrize("score", [-1, -0.5, 100.5, 101, 1000])
def test_invalid(score):
    assert letter_grade(score) == "invalid", (
        f"{score} is outside 0..100, so return 'invalid'. Check this FIRST, before the grades.")
