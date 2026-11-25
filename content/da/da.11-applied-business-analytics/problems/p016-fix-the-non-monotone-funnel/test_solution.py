import numpy as np
import pandas as pd
import pytest

from solution import funnel_table

STEPS = ["viewed", "carted", "bought"]
#                 viewed  carted  bought
ROWS = [(True, True, True), (True, True, False), (True, False, False), (False, False, False),
        (True, False, True), (False, True, True), (True, True, True), (False, False, True)]
DF = pd.DataFrame(ROWS, columns=STEPS)


def test_no_step_exceeds_the_previous_one():
    t, _ = funnel_table(DF, STEPS)
    assert t["sessions"].tolist() == [8, 5, 3, 2], f"nested counts 8, 5, 3, 2 (a session counts only if it passed every earlier step), got {t['sessions'].tolist()}"
    assert (t["% of previous step"].dropna() <= 100).all(), "no step may be above 100% of the previous one."


def test_percentages_and_dropped():
    t, _ = funnel_table(DF, STEPS)
    assert t["% of previous step"].iloc[1:].tolist() == pytest.approx([62.5, 60.0, 200 / 3]), "5/8, 3/5, 2/3."
    assert t["% of all sessions"].tolist() == pytest.approx([100.0, 62.5, 37.5, 25.0])
    assert t["dropped"].iloc[1:].tolist() == [3, 2, 1] and pd.isna(t.loc[0, "dropped"])
    assert list(t.columns) == ["step", "sessions", "% of previous step", "% of all sessions", "dropped"]


def test_number_of_inconsistent_sessions():
    _, bad = funnel_table(DF, STEPS)
    assert bad == 3, f"sessions 5, 6 and 8 have a later step True after an earlier one False: 3, got {bad}"


def test_a_clean_table_has_no_inconsistent_sessions():
    clean = pd.DataFrame([(True, True, True), (True, True, False), (True, False, False), (False, False, False)], columns=STEPS)
    t, bad = funnel_table(clean, STEPS)
    assert bad == 0 and t["sessions"].tolist() == [4, 3, 2, 1], "consistent data: the same counts as the simple method, 0 inconsistent."
    assert isinstance(bad, int), "return a plain int."
