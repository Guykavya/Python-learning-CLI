import numpy as np
import pytest

from solution import confusion_at

Y = [1, 0, 1, 0, 1, 0]
P = [0.9, 0.8, 0.6, 0.4, 0.3, 0.1]


def test_worked_example():
    assert confusion_at(Y, P, 0.5) == {"TP": 2, "FP": 1, "FN": 1, "TN": 2}, "at 0.5 rows 0, 1, 2 are predicted positive; row 1 is a false positive, row 4 a false negative."


def test_threshold_zero_means_everyone_positive():
    assert confusion_at(Y, P, 0.0) == {"TP": 3, "FP": 3, "FN": 0, "TN": 0}, "threshold 0: every probability is >= 0, so everyone is predicted positive."


def test_threshold_one_means_nobody_positive():
    assert confusion_at(Y, P, 1.0) == {"TP": 0, "FP": 0, "FN": 3, "TN": 3}, "threshold 1: no probability below 1 is >= 1, so nobody is predicted positive."


def test_equal_to_threshold_is_positive():
    assert confusion_at([1], [0.6], 0.6) == {"TP": 1, "FP": 0, "FN": 0, "TN": 0}, "p exactly equal to the threshold counts as positive (>=)."


def test_counts_add_up_and_are_ints():
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 100)
    p = rng.random(100)
    out = confusion_at(y, p, 0.37)
    assert sum(out.values()) == 100, "the four counts must add up to the number of rows."
    assert all(type(v) is int for v in out.values()), "return plain ints."
    assert out["TP"] + out["FN"] == int(y.sum()), "TP + FN is the number of actual positives."


def test_accepts_numpy_and_lists():
    assert confusion_at(np.array(Y), np.array(P), 0.5) == confusion_at(Y, P, 0.5), "lists and arrays must give the same answer."
