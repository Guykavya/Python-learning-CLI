import pytest

from solution import break_even_ratio, hit_ratio, mean_latency


def test_hit_ratio_basic():
    assert hit_ratio(["hit", "hit", "miss", "hit"]) == pytest.approx(0.75), "3 hits out of 4 events is 0.75."


def test_hit_ratio_all_or_nothing():
    assert hit_ratio(["miss"] * 5) == 0.0, "No hits gives 0.0."
    assert hit_ratio(["hit"] * 5) == 1.0, "Only hits gives 1.0."


def test_hit_ratio_empty():
    assert hit_ratio([]) == 0.0, "No events yet: return 0.0, do not divide by zero."


def test_hit_ratio_rejects_unknown_event():
    with pytest.raises(ValueError, match="HIT"):
        hit_ratio(["hit", "HIT"])
    # The message must name the bad value so the person reading the log can find it.


def test_mean_latency():
    assert mean_latency(0.75, 1, 40) == pytest.approx(11.0), "1 ms lookup for everyone + 25% of requests pay 40 ms = 11 ms."
    assert mean_latency(1.0, 1, 40) == pytest.approx(1.0), "All hits: only the lookup."


def test_useless_cache_is_slower():
    assert mean_latency(0.0, 1, 40) == pytest.approx(41.0), \
        "With no hits every request pays the lookup AND the database: 41 ms, worse than no cache (40 ms)."


def test_mean_latency_rejects_bad_ratio():
    for bad in (-0.1, 1.5):
        with pytest.raises(ValueError):
            mean_latency(bad, 1, 40)


def test_break_even():
    assert break_even_ratio(1, 40) == pytest.approx(0.025), "lookup + (1 - r) * db = db  ->  r = lookup / db = 1/40."
    r = break_even_ratio(2, 10)
    assert mean_latency(r, 2, 10) == pytest.approx(10), "At the break-even ratio the cache must be exactly as fast as the database."


def test_break_even_impossible():
    assert break_even_ratio(5, 5) is None, "A lookup as slow as the database can never pay off: return None."
    assert break_even_ratio(8, 5) is None, "A lookup slower than the database can never pay off: return None."
