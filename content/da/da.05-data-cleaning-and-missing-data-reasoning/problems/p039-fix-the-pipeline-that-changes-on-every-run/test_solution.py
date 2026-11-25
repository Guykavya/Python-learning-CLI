import numpy as np
import pandas as pd
import pytest

import solution
from solution import clean


def frame():
    return pd.DataFrame({"item": ["a", "b", "c"], "weight_g": [1500.0, 250.0, 40.0], "price": [10.0, np.nan, 30.0]},
                        index=[5, 6, 7])


def test_the_output_is_right_the_first_time():
    out = clean(frame(), [])
    assert list(out.columns) == ["item", "weight_kg", "price"], "output columns: item, weight_kg, price. Got %s." % list(out.columns)
    assert out["weight_kg"].tolist() == pytest.approx([1.5, 0.25, 0.04]), "weight_kg = weight_g / 1000 (1500 g is 1.5 kg)."
    assert out["price"].tolist() == pytest.approx([10.0, 20.0, 30.0]), "the missing price becomes the median of the observed prices (20)."
    assert out.index.tolist() == [5, 6, 7], "keep the index of df."


def test_running_twice_gives_the_same_output():
    df = frame()
    first = clean(df, [])
    second = clean(df, [])
    assert second["weight_kg"].tolist() == pytest.approx(first["weight_kg"].tolist()), (
        "the second run gave different weights: %s instead of %s. Is the unit conversion applied to the caller's frame, so "
        "it is divided by 1000 again on the next call?" % (second["weight_kg"].tolist(), first["weight_kg"].tolist()))
    pd.testing.assert_frame_equal(first, second, obj="two runs on the same input (idempotence)")


def test_the_input_frame_is_not_changed():
    df = frame()
    before = df.copy()
    clean(df, [])
    pd.testing.assert_frame_equal(df, before, obj="the caller's frame after clean (do not convert or fill it in place; "
                                                  "copy first)")


def test_the_log_is_only_the_one_passed_in():
    log = []
    clean(frame(), log)
    assert log == [{"step": "clean", "rows": 3, "price_filled": 1}], (
        "write exactly one line to the log list that was passed in: {'step': 'clean', 'rows': 3, 'price_filled': 1}. Got %s." % log)


def test_no_hidden_global_log():
    module_log = getattr(solution, "LOG", [])
    n = len(module_log)
    clean(frame(), [])
    clean(frame(), [])
    assert len(getattr(solution, "LOG", [])) == n, (
        "clean must not append to a module-level list: it remembers between runs. Use only the `log` argument.")


def test_two_calls_two_lines_and_the_second_count_is_still_right():
    log = []
    df = frame()
    clean(df, log)
    clean(df, log)
    assert [r["price_filled"] for r in log] == [1, 1], (
        "both runs started from the same input, so both fill one price. Got %s (if the second is 0, the first run filled the "
        "caller's frame)." % [r["price_filled"] for r in log])


def test_nothing_to_fill():
    d = pd.DataFrame({"item": ["a"], "weight_g": [500.0], "price": [4.0]})
    log = []
    out = clean(d, log)
    assert out["price"].tolist() == [4.0] and log[0]["price_filled"] == 0
