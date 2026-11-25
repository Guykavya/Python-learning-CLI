import numpy as np
import pandas as pd
import pytest

from solution import check_report

GOOD = """# Monthly churn rose from 4.0% to 5.7%

![Churn and on-time delivery](overview.png)

Late boxes explain 1.4 points.

![Contributions](contributions.png)

Data to: 2024-12-30
"""
NUMBERS = {"churn_before": "4.0%", "churn_after": "5.7%", "late_pts": "1.4 points"}


@pytest.fixture
def figs(tmp_path):
    for name in ("overview.png", "contributions.png"):
        (tmp_path / name).write_bytes(b"png")
    return tmp_path


def test_good_report(figs):
    assert check_report(GOOD, NUMBERS, figs, "2024-12-30") == [], f"a correct report has no problems, got {check_report(GOOD, NUMBERS, figs, '2024-12-30')}"


def test_wrong_number(figs):
    bad = GOOD.replace("5.7%", "5.1%")
    assert check_report(bad, NUMBERS, figs, "2024-12-30") == ["churn_after = 5.7% does not appear in the text"]


def test_placeholder_and_todo_reported_once(figs):
    bad = GOOD + "\n{saved} customers TODO\n"
    assert check_report(bad, NUMBERS, figs, "2024-12-30") == ["unfilled template placeholder or TODO left in the text"], "report the leftover once."


def test_missing_and_unused_figures(figs):
    bad = GOOD.replace("contributions.png", "missing.png")
    (figs / "extra.png").write_bytes(b"png")
    assert check_report(bad, NUMBERS, figs, "2024-12-30") == [
        "figure file missing: missing.png",
        "figure not used in the text: contributions.png",
        "figure not used in the text: extra.png",
    ], f"got {check_report(bad, NUMBERS, figs, '2024-12-30')}"


def test_dates(figs):
    assert check_report(GOOD, NUMBERS, figs, "2025-01-06") == ["stale date: text says 2024-12-30, data run to 2025-01-06"]
    no_line = GOOD.replace("Data to: 2024-12-30\n", "")
    assert check_report(no_line, NUMBERS, figs, "2024-12-30") == ["no 'Data to:' line"]


def test_order_of_problems(figs):
    bad = GOOD.replace("4.0%", "4.2%").replace("overview.png", "gone.png").replace("2024-12-30", "2024-11-30") + "TODO"
    assert check_report(bad, NUMBERS, figs, "2024-12-30") == [
        "churn_before = 4.0% does not appear in the text",
        "unfilled template placeholder or TODO left in the text",
        "figure file missing: gone.png",
        "figure not used in the text: overview.png",
        "stale date: text says 2024-11-30, data run to 2024-12-30",
    ], f"checks in the stated order, got {check_report(bad, NUMBERS, figs, '2024-12-30')}"
