import numpy as np
import pandas as pd
import pytest

from solution import headline


def test_rise_with_cause():
    got = headline("Monthly churn", 4.04, 5.68, "Sep-Dec 2024", "late deliveries more than doubled")
    assert got == "Monthly churn rose from 4.0% to 5.7% in Sep-Dec 2024, mainly because late deliveries more than doubled", f"got {got!r}"


def test_fall_without_cause():
    got = headline("On-time delivery", 92.0, 79.8, "September 2024")
    assert got == "On-time delivery fell from 92.0% to 79.8% in September 2024", f"no cause: no ', mainly because'; got {got!r}"


def test_rounded_equal_means_stayed():
    got = headline("Churn", 4.04, 4.01, "October")
    assert got == "Churn stayed at 4.0% in October", f"4.04 and 4.01 both read 4.0: say 'stayed at', got {got!r}"


def test_other_unit():
    got = headline("Weekly revenue", 3068.18, 3603.5, "2024", unit=" thousand rupees")
    assert got == "Weekly revenue rose from 3068.2 thousand rupees to 3603.5 thousand rupees in 2024", f"the unit follows each number, got {got!r}"


def test_too_long():
    cause = " ".join(["word"] * 40)
    with pytest.raises(ValueError, match=r"headline is \d+ words \(more than 40\)"):
        headline("Churn", 4.0, 5.0, "2024", cause)
