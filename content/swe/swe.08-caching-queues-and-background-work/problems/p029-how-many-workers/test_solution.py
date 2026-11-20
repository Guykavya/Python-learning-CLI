import math

import pytest

from solution import admit, drain_seconds, workers_needed


def test_workers_basic():
    assert workers_needed(20, 0.5) == 15, "20 jobs/s x 0.5 s = 10 busy; 10 / 0.7 = 14.29 -> 15 workers."


def test_workers_full_utilisation():
    assert workers_needed(20, 0.5, target_utilisation=1.0) == 10, "At 100% target, workers = busy = 10 (no headroom)."


def test_workers_float_trap():
    assert workers_needed(14, 1.5) == 30, "busy = 21 and 21 / 0.7 is 30.000000000000004 in floats: round to 9 decimals before ceil, or you get 31."
    assert workers_needed(7, 0.3) == 3, "busy = 2.1 and 2.1 / 0.7 is 3.0000000000000004 in floats: the answer is 3, not 4."


def test_workers_at_least_one():
    assert workers_needed(0, 2) == 1, "No traffic still needs one worker."
    assert workers_needed(0.1, 0.1) == 1


def test_workers_bad_input():
    for bad in (0, -0.5, 1.5):
        with pytest.raises(ValueError):
            workers_needed(10, 1, target_utilisation=bad)
    with pytest.raises(ValueError):
        workers_needed(-1, 1)


def test_drain():
    assert drain_seconds(4440, 20, 26) == pytest.approx(740.0), "4440 jobs / (26 - 20) per second = 740 s."
    assert drain_seconds(0, 20, 10) == 0.0, "An empty backlog is already drained."


def test_never_drains():
    assert drain_seconds(4440, 20, 20) == math.inf, "Capacity equal to the arrival rate never shrinks the backlog: inf."
    assert drain_seconds(10, 30, 20) == math.inf, "Capacity below the arrival rate: the backlog grows for ever."


def test_admit():
    assert admit(2, 3) == (202, {}), "Below the limit: accept (202) with no extra headers."
    assert admit(3, 3) == (503, {"Retry-After": "30"}), "At the limit: refuse with 503 and Retry-After (a string)."
    assert admit(10, 3, retry_after=60) == (503, {"Retry-After": "60"})
