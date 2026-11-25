import pandas as pd
import pytest

from solution import assert_rows_unchanged


def frame(n):
    return pd.DataFrame({"id": list(range(n))})


def test_equal_counts_return_after_itself():
    before, after = frame(5), frame(5)
    out = assert_rows_unchanged(before, after, "jobs + customers")
    assert out is after, "when nothing changed, return the `after` frame itself so the call can sit inside a pipeline."


def test_more_rows_is_a_fan_out():
    with pytest.raises(AssertionError) as e:
        assert_rows_unchanged(frame(120), frame(134), "jobs + payments")
    assert str(e.value) == "fan-out in jobs + payments: 120 → 134 rows", (
        "growing from 120 to 134 rows must say exactly 'fan-out in jobs + payments: 120 → 134 rows'. Got: %s" % e.value)


def test_fewer_rows_is_a_lost_key():
    with pytest.raises(AssertionError) as e:
        assert_rows_unchanged(frame(120), frame(100), "jobs + payments")
    assert str(e.value) == "rows lost in jobs + payments: 120 → 100 rows", (
        "shrinking is a different problem (an inner join dropped rows); say 'rows lost in <label>: 120 → 100 rows'. Got: %s" % e.value)


def test_label_appears_in_the_message():
    with pytest.raises(AssertionError, match="items"):
        assert_rows_unchanged(frame(2), frame(5), "items")


def test_empty_frames_are_fine():
    assert assert_rows_unchanged(frame(0), frame(0), "x") is not None, "0 rows before and after is unchanged, not an error."


def test_real_left_join_fan_out_is_caught():
    jobs = pd.DataFrame({"job_id": [1, 2, 3]})
    payments = pd.DataFrame({"job_id": [1, 1, 2], "amount": [300, 700, 400]})      # job 1 pays twice
    joined = jobs.merge(payments, on="job_id", how="left")
    with pytest.raises(AssertionError, match="3 → 4 rows"):
        assert_rows_unchanged(jobs, joined, "jobs + payments")


def test_frames_are_not_changed():
    a, b = frame(3), frame(3)
    assert_rows_unchanged(a, b, "x")
    assert len(a) == 3 and len(b) == 3
