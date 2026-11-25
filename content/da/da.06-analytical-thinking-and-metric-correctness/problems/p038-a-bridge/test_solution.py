import pytest

from solution import bridge

STEPS = [("ops only: completed in Feb, paid later", -20), ("finance only: paid in Feb, completed in Jan", +29)]
GOOD = ("step | change | running | check\n"
        "jobs completed in Feb |  | 807 |\n"
        "ops only: completed in Feb, paid later | -20 | 787 |\n"
        "finance only: paid in Feb, completed in Jan | +29 | 816 |\n"
        "= jobs paid in Feb |  | 816 | OK")


def test_the_whole_table():
    got = bridge("jobs completed in Feb", 807, STEPS, "jobs paid in Feb", 816)
    assert got == GOOD, ("the table must match exactly (cells joined with ' | ', signed changes, running totals, 'OK' on the last line, "
                         "every line right-stripped, no final newline). Got:\n%s" % got)


def test_no_trailing_spaces_and_no_final_newline():
    got = bridge("a", 10, [("x", 5)], "b", 15)
    assert all(line == line.rstrip() for line in got.split("\n")), "strip trailing spaces from every line."
    assert not got.endswith("\n"), "no newline at the end."


def test_signs_and_zero_step():
    got = bridge("start", 100, [("down", -30), ("flat", 0), ("up", 5)], "end", 75)
    lines = got.split("\n")
    assert lines[2] == "down | -30 | 70 |" and lines[3] == "flat | +0 | 70 |" and lines[4] == "up | +5 | 75 |", (
        "write the change with an explicit sign (f'{change:+d}': +5, -30, +0) and the running total after it. Got %s." % lines)


def test_no_steps_start_equals_end():
    got = bridge("same", 5, [], "same again", 5)
    assert got == "step | change | running | check\nsame |  | 5 |\n= same again |  | 5 | OK", "an empty bridge is just start and end. Got %r." % got


def test_unexplained_gap_raises_with_sign():
    with pytest.raises(ValueError) as e:
        bridge("A", 807, [("one", -20)], "B", 800)
    assert str(e.value) == "UNEXPLAINED -13: bridge from A does not reach B", (
        "the steps reach 787 but the end is 800: gap = running total - end = -13, written with a sign. Got %r." % str(e.value))
    with pytest.raises(ValueError) as e2:
        bridge("A", 807, [("one", +9)], "B", 813)
    assert str(e2.value) == "UNEXPLAINED +3: bridge from A does not reach B", "816 reached, 813 expected: gap +3. Got %r." % str(e2.value)


def test_a_bridge_that_closes_never_raises_and_a_wrong_step_is_caught():
    bridge("A", 10, [("p", 3), ("q", -1)], "B", 12)
    with pytest.raises(ValueError):
        bridge("A", 10, [("p", 3), ("q", -2)], "B", 12)
