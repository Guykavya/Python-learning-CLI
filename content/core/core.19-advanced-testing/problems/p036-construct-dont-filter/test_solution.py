import ast
from pathlib import Path

from hypothesis import given, settings, strategies as st
from hypothesis.errors import FailedHealthCheck
from hypothesis.strategies import SearchStrategy

import solution

SOURCE = Path(solution.__file__).read_text()


def draw(name):
    strategy = getattr(solution, name, None)
    assert strategy is not None, f"solution.py must define a variable called {name}."
    assert isinstance(strategy, SearchStrategy), f"{name} must be a hypothesis strategy."
    seen = []

    @settings(derandomize=True, database=None, max_examples=100)
    @given(strategy)
    def probe(value):
        seen.append(value)

    try:
        probe()
    except FailedHealthCheck as error:
        raise AssertionError(
            f"hypothesis gave up on {name}: it had to throw away almost every example it generated "
            "(a .filter() or assume() that rejects too much). Build the values instead of rejecting them. "
            f"({str(error).splitlines()[0]})") from None
    return seen


def test_no_filter_and_no_assume():
    tree = ast.parse(SOURCE)
    used = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Attribute) and f.attr in ("filter", "example"):
                used.append(f".{f.attr}()")
            if (isinstance(f, ast.Name) and f.id == "assume") or (isinstance(f, ast.Attribute) and f.attr == "assume"):
                used.append("assume()")
    assert not used, (
        f"Your strategies still use {sorted(set(used))}. The point of this problem is to CONSTRUCT valid values "
        "(with .map, tuples, lists(..., unique=True), bounds) instead of generating anything and rejecting the bad ones.")


def test_even_numbers():
    seen = draw("even_numbers")
    bad = [x for x in seen if type(x) is not int or x % 2 != 0 or not -1000 <= x <= 1000]
    assert not bad, (f"even_numbers must give EVEN whole numbers from -1000 to 1000; it gave {bad[:5]}. "
                     "Idea: pick any integer from -500 to 500 and double it with .map.")
    assert any(x < 0 for x in seen) and any(x > 0 for x in seen), "even_numbers should be negative and positive."
    assert len(set(seen)) >= 20, "even_numbers should give many different numbers."


def test_sorted_lists():
    seen = draw("sorted_lists")
    bad = [x for x in seen if not (isinstance(x, list) and len(x) <= 10 and all(type(v) is int and -50 <= v <= 50 for v in x)
                                   and all(a <= b for a, b in zip(x, x[1:])))]
    assert not bad, (f"sorted_lists must give lists of at most 10 whole numbers from -50 to 50 in ascending order; it gave {bad[:3]}. "
                     "Idea: generate any list of such numbers and sort it with .map(sorted).")
    assert any(len(x) == 0 for x in seen) and any(len(x) >= 5 for x in seen), "Both empty and longer lists should appear."
    assert any(len(x) != len(set(x)) for x in seen), "Lists with repeated numbers should appear too (equal neighbours are allowed)."


def test_ordered_pairs():
    seen = draw("ordered_pairs")
    bad = [p for p in seen if not (isinstance(p, tuple) and len(p) == 2 and all(type(v) is int for v in p)
                                   and -100 <= p[0] <= 100 and 1 <= p[1] - p[0] <= 50)]
    assert not bad, (f"ordered_pairs must give tuples (a, b) of whole numbers with a from -100 to 100 and b - a from 1 to 50; it gave {bad[:3]}. "
                     "Idea: generate a and a gap separately, then build b = a + gap with .map.")
    assert any(p[1] - p[0] == 1 for p in seen) and any(p[1] - p[0] >= 30 for p in seen), "Small and large gaps should both appear."


def test_multiples_of_1000():
    seen = draw("multiples_of_1000")
    bad = [x for x in seen if type(x) is not int or x % 1000 != 0 or not -1_000_000 <= x <= 1_000_000]
    assert not bad, (f"multiples_of_1000 must give multiples of 1000 from -1,000,000 to 1,000,000; it gave {bad[:5]}. "
                     "Idea: a small integer times 1000.")
    assert len(set(seen)) >= 20, "multiples_of_1000 should give many different values."


def test_distinct_lists():
    seen = draw("distinct_lists")
    bad = [x for x in seen if not (isinstance(x, list) and 2 <= len(x) <= 8 and len(set(x)) == len(x)
                                   and all(type(v) is int and -20 <= v <= 20 for v in x))]
    assert not bad, (f"distinct_lists must give lists of 2 to 8 DIFFERENT whole numbers from -20 to 20; it gave {bad[:3]}. "
                     "st.lists has an argument for exactly this.")
    assert {len(x) for x in seen} >= {2, 8}, "Lists of length 2 and of length 8 should both appear."
