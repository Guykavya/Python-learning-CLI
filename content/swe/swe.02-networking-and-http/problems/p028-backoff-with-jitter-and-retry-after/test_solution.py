import random
from datetime import datetime, timezone

import pytest

from solution import delays, retry_after

NOW = datetime(2026, 11, 7, 10, 0, 0, tzinfo=timezone.utc)


class TopRng:
    """uniform(a, b) returns the ceiling b and records the calls."""

    def __init__(self):
        self.calls = []

    def uniform(self, a, b):
        self.calls.append((a, b))
        return b


def test_ceilings_double_and_stop_at_the_cap():
    rng = TopRng()
    out = delays(6, 0.5, 8.0, rng)
    assert rng.calls == [(0, 0.5), (0, 1.0), (0, 2.0), (0, 4.0), (0, 8.0), (0, 8.0)], (
        f"Draw rng.uniform(0, min(cap, base * 2**i)) for i = 0, 1, 2, ...; got {rng.calls}.")
    assert out == [0.5, 1.0, 2.0, 4.0, 8.0, 8.0]


def test_zero_attempts():
    assert delays(0, 1, 5, random.Random(0)) == []


def test_values_stay_inside_the_bounds_for_many_seeds():
    for seed in range(50):
        out = delays(10, 0.25, 4.0, random.Random(seed))
        assert len(out) == 10
        for i, v in enumerate(out):
            assert 0 <= v <= min(4.0, 0.25 * 2 ** i), f"seed {seed}, retry {i}: {v} is outside [0, ceiling]."


def test_jitter_really_varies():
    runs = {tuple(delays(5, 1.0, 100.0, random.Random(s))) for s in range(20)}
    assert len(runs) > 15, "With different seeds the waits must differ: that is the jitter."
    assert len({round(v, 6) for v in delays(10, 1.0, 100.0, random.Random(1))}) == 10


def test_same_seed_same_delays():
    assert delays(5, 0.5, 8, random.Random(7)) == delays(5, 0.5, 8, random.Random(7))


def test_retry_after_seconds():
    assert retry_after("30", NOW) == 30
    assert retry_after("0", NOW) == 0
    assert retry_after(" 12 ", NOW) == 12


def test_retry_after_date():
    assert retry_after("Sat, 07 Nov 2026 10:00:30 GMT", NOW) == 30
    assert retry_after("Sat, 07 Nov 2026 10:02:00 GMT", NOW) == 120
    assert retry_after("Sat, 07 Nov 2026 09:00:00 GMT", NOW) == 0, "A date in the past is 0, never negative."


@pytest.mark.parametrize("bad", [None, "", "soon", "-5", "1.5", "Tomorrow-ish", "30s"])
def test_unusable_values_give_none(bad):
    assert retry_after(bad, NOW) is None


def test_cap():
    assert retry_after("86400", NOW, cap=60) == 60, "Never trust a server that says 'wait a day'."
    assert retry_after("20", NOW, cap=60) == 20
    assert retry_after("Sun, 08 Nov 2026 10:00:00 GMT", NOW, cap=120) == 120
    assert retry_after("86400", NOW) == 86400, "No cap given: no limit."
