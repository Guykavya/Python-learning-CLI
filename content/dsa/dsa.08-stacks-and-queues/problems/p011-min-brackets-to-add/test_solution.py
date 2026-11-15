import itertools

import pytest

from solution import brackets_to_add


@pytest.mark.parametrize("s, want, why", [
    ("", (0, 0), "nothing to fix"),
    ("()", (0, 0), "already balanced"),
    ("())", (1, 0), "one ) too many: it needs a ( before it"),
    ("(((", (0, 3), "three ( are never closed"),
    (")))", (3, 0), "three ) with nothing to close: each needs a ( before it"),
    ("()))((", (2, 2), "both directions at once"),
    (")(", (1, 1), "equal counts but in the wrong order: a ( cannot close a ) that came before it"),
    ("(()))(", (1, 1), "one ) too many in the middle and one ( open at the end"),
    ("))((()", (2, 2), "do not let the counter go below zero: the two ) need two (, and two ( stay open"),
])
def test_cases(s, want, why):
    got = brackets_to_add(s)
    assert got == want, f"brackets_to_add({s!r}) should be {want} (opens, closes), got {got}: {why}."


def balanced(t):
    depth = 0
    for ch in t:
        depth += 1 if ch == "(" else -1
        if depth < 0:
            return False
    return depth == 0


def test_all_short_strings_are_minimal():
    for n in range(0, 9):
        for chars in itertools.product("()", repeat=n):
            s = "".join(chars)
            a, b = brackets_to_add(s)
            assert balanced("(" * a + s + ")" * b), (
                f"For {s!r} you said ({a}, {b}), but adding them still does not balance it.")
            best = min(x + y for x in range(n + 1) for y in range(n + 1) if balanced("(" * x + s + ")" * y))
            assert a + b == best, f"For {s!r} the minimum is {best} insertions, you said {a + b}."


def test_long():
    assert brackets_to_add(")" * 50000 + "(" * 50000) == (50000, 50000), "100,000 characters, both kinds of imbalance."
