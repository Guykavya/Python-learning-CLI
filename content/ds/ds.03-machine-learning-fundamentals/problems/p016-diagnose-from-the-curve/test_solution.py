import pandas as pd
import pytest

from solution import diagnose


def curve(rows):
    df = pd.DataFrame(rows, columns=["n_train", "train", "validation"])
    df["gap"] = df["validation"] - df["train"]
    return df


def test_high_variance():
    lc = curve([(10, 0.0, 2.0), (50, 0.03, 1.2), (200, 0.05, 0.90)])
    assert diagnose(lc) == "high variance", "a validation error of 0.90 against a training error of 0.05 is a huge relative gap: high variance."


def test_high_bias_needs_the_floor():
    lc = curve([(10, 0.45, 0.60), (50, 0.50, 0.55), (200, 0.50, 0.53)])
    assert diagnose(lc, floor=0.30) == "high bias", "small gap but an error (0.53) far above the 0.30 floor: high bias."
    assert diagnose(lc) == "fine", "without a floor a small gap is called fine."


def test_fine():
    lc = curve([(10, 0.20, 0.45), (50, 0.27, 0.34), (200, 0.29, 0.31)])
    assert diagnose(lc, floor=0.30) == "fine", "0.31 is within 25% of the floor and the gap is small."


def test_only_the_last_row_counts():
    lc = curve([(10, 0.0, 5.0), (200, 0.29, 0.31)])
    assert diagnose(lc, floor=0.30) == "fine", "use the last row only; the huge gap at n = 10 is history."


def test_classification_uses_one_minus_accuracy():
    lc = pd.DataFrame({"n_train": [100, 400], "train": [1.0, 1.0], "validation": [0.85, 0.90]})
    lc["gap"] = lc["train"] - lc["validation"]
    assert diagnose(lc, "classification") == "high variance", "validation error is 1 - 0.90 = 0.10; the gap 0.10 is a relative gap of 1.0."


def test_unknown_task():
    with pytest.raises(ValueError):
        diagnose(curve([(10, 0.1, 0.2)]), "ranking")
