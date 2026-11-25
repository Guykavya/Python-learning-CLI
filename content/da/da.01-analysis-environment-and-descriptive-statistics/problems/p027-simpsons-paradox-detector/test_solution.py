import pytest

from solution import rates_by_group


def rows_from(counts):
    """counts: {(group, treatment): (successes, total)} -> list of rows."""
    rows = []
    for (group, treatment), (successes, total) in counts.items():
        rows += [(group, treatment, True)] * successes + [(group, treatment, False)] * (total - successes)
    return rows


KIDNEY = {("small", "A"): (81, 87), ("small", "B"): (234, 270), ("large", "A"): (192, 263), ("large", "B"): (55, 80)}


def test_kidney_stone_numbers():
    got = rates_by_group(rows_from(KIDNEY))
    assert got["groups"]["small"]["A"] == pytest.approx(81 / 87, rel=1e-9), "Group rate = successes / rows inside the group."
    assert got["groups"]["large"]["B"] == pytest.approx(55 / 80, rel=1e-9), "Group rate = successes / rows inside the group."
    assert got["overall"]["A"] == pytest.approx(273 / 350, rel=1e-9), "Overall A = 273 of 350 (do not average the group rates)."
    assert got["overall"]["B"] == pytest.approx(289 / 350, rel=1e-9), "Overall B = 289 of 350."
    assert got["paradox"] is True, "A wins both groups, B wins overall: that is Simpson's paradox."


def test_mirrored_paradox():
    mirrored = {(g, "B" if t == "A" else "A"): v for (g, t), v in KIDNEY.items()}
    assert rates_by_group(rows_from(mirrored))["paradox"] is True, "The mirrored case (B wins every group, A wins overall) is also a paradox."


def test_no_paradox_when_the_total_agrees():
    counts = {("x", "A"): (90, 100), ("x", "B"): (80, 100), ("y", "A"): (50, 100), ("y", "B"): (40, 100)}
    got = rates_by_group(rows_from(counts))
    assert got["paradox"] is False, "A wins both groups and overall: no paradox."
    assert got["overall"]["A"] > got["overall"]["B"]


def test_no_paradox_when_groups_disagree():
    counts = {("x", "A"): (90, 100), ("x", "B"): (80, 100), ("y", "A"): (40, 100), ("y", "B"): (50, 100)}
    assert rates_by_group(rows_from(counts))["paradox"] is False, "The groups disagree with each other: that is not the paradox."


def test_a_tie_is_not_a_preference():
    counts = {("x", "A"): (50, 100), ("x", "B"): (50, 100), ("y", "A"): (10, 100), ("y", "B"): (5, 10)}
    assert rates_by_group(rows_from(counts))["paradox"] is False, "A tie in a group means the group does not prefer one treatment."


def test_row_order_does_not_matter():
    rows = rows_from(KIDNEY)
    assert rates_by_group(list(reversed(rows))) == rates_by_group(rows), "The result must not depend on the order of the rows."


def test_errors():
    with pytest.raises(ValueError):
        rates_by_group([])
    with pytest.raises(ValueError):
        rates_by_group([("g", "C", True)])
    with pytest.raises(ValueError):
        rates_by_group([("g", "A", True), ("g", "A", False)])
