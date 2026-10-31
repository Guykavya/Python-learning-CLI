import math
import string

from hypothesis import given, settings, strategies as st
from hypothesis.strategies import SearchStrategy

import solution
from solution import Point

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def draw(name):
    """Draw 100 examples (always the same ones: derandomize=True) from the strategy called `name`."""
    strategy = getattr(solution, name, None)
    assert strategy is not None, f"solution.py must define a variable called {name}."
    assert isinstance(strategy, SearchStrategy), (
        f"{name} must be a hypothesis strategy (something like st.integers(...)), not {type(strategy).__name__}.")
    seen = []

    @settings(derandomize=True, database=None, max_examples=100)
    @given(strategy)
    def probe(value):
        seen.append(value)

    probe()
    return seen


def test_small_ints():
    seen = draw("small_ints")
    bad = [x for x in seen if type(x) is not int or not 1 <= x <= 100]
    assert not bad, f"small_ints must give whole numbers from 1 to 100 inclusive; it gave {bad[:5]}. Use st.integers(min_value=..., max_value=...)."
    assert min(seen) <= 5 and max(seen) >= 95, "small_ints should cover the whole range 1..100, not a corner of it."


def test_usernames():
    seen = draw("usernames")
    bad = [x for x in seen if not (isinstance(x, str) and 3 <= len(x) <= 12 and all(c in string.ascii_lowercase for c in x))]
    assert not bad, (f"usernames must be 3 to 12 lowercase ASCII letters (a-z), nothing else; it gave {bad[:5]!r}. "
                     "Use st.text(alphabet=string.ascii_lowercase, min_size=3, max_size=12).")
    lengths = {len(x) for x in seen}
    assert min(lengths) <= 4 and max(lengths) >= 10, "usernames should use short and long names, not one length."


def test_digit_lists():
    seen = draw("digit_lists")
    bad = [x for x in seen if not (isinstance(x, list) and 1 <= len(x) <= 5 and all(type(d) is int and 0 <= d <= 9 for d in x))]
    assert not bad, (f"digit_lists must give lists of 1 to 5 digits (whole numbers 0..9); it gave {bad[:3]}. "
                     "Use st.lists(st.integers(0, 9), min_size=1, max_size=5).")
    assert {len(x) for x in seen} >= {1, 5}, "digit_lists should produce lists of length 1 and of length 5 among its examples."
    assert {d for x in seen for d in x} >= {0, 9}, "Both digits 0 and 9 should show up."


def test_stock():
    seen = draw("stock")
    def ok_key(k):
        return isinstance(k, str) and 1 <= len(k) <= 5 and all(c in string.ascii_lowercase for c in k)
    def ok_value(v):
        return isinstance(v, float) and math.isfinite(v) and 0 <= v <= 100
    bad = [d for d in seen if not (isinstance(d, dict) and 1 <= len(d) <= 4
                                   and all(ok_key(k) and ok_value(v) for k, v in d.items()))]
    assert not bad, (f"stock must be a dict with 1 to 4 entries: keys 1-5 lowercase letters, values floats from 0 to 100 "
                     f"(no nan, no infinity); it gave {bad[:2]}. Use st.dictionaries(keys, st.floats(0, 100), min_size=1, max_size=4).")
    values = [v for d in seen for v in d.values()]
    assert any(v != int(v) for v in values), "The prices should include numbers with decimals, not only whole numbers."
    assert {len(d) for d in seen} >= {1, 4}, "stock should have dictionaries with 1 entry and with 4 entries."


def test_points():
    seen = draw("points")
    bad = [p for p in seen if not (isinstance(p, Point) and type(p.x) is int and type(p.y) is int
                                   and -10 <= p.x <= 10 and -10 <= p.y <= 10)]
    assert not bad, (f"points must give Point objects with whole-number x and y from -10 to 10; it gave {bad[:3]}. "
                     "Use st.builds(Point, x=st.integers(-10, 10), y=st.integers(-10, 10)).")
    assert any(p.x < 0 for p in seen) and any(p.x > 0 for p in seen) and any(p.y < 0 for p in seen), (
        "points should have negative and positive coordinates.")


def test_id_or_none():
    seen = draw("id_or_none")
    bad = [x for x in seen if not (x is None or (type(x) is int and 1 <= x <= 999))]
    assert not bad, (f"id_or_none must give None or a whole number from 1 to 999; it gave {bad[:5]}. "
                     "Combine two strategies with st.one_of(st.none(), st.integers(1, 999)).")
    assert any(x is None for x in seen) and any(x is not None for x in seen), (
        "id_or_none must give both None and numbers among its examples.")
    assert len({x for x in seen if x is not None}) >= 5, "The numbers should vary."


def test_weekdays():
    seen = draw("weekdays")
    bad = [x for x in seen if x not in DAYS]
    assert not bad, f"weekdays must give one of {DAYS}; it gave {bad[:5]!r}. Use st.sampled_from(DAYS)."
    assert set(seen) == set(DAYS), "All seven days should appear among the examples."
