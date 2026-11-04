import subprocess
import sys
from pathlib import Path

import pytest

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or a loop that does far more work than needed.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import random


import ast

BANNED = ('sorted', 'heapq', 'bisect', 'cmp_to_key')


def test_no_builtin_sorting():
    tree = ast.parse(SOLUTION.read_text())
    bad = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in BANNED:
            bad.add(node.id)
        if isinstance(node, ast.Attribute) and (node.attr == "sort" or node.attr in BANNED):
            bad.add("." + node.attr)
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mods = [a.name for a in node.names] + [getattr(node, "module", None) or ""]
            for m in mods:
                if m.split(".")[0] in BANNED:
                    bad.add(m)
    assert not bad, (
        f"This problem is about BUILDING the sort yourself: found {sorted(bad)} in your code. "
        "Write the loops and comparisons by hand; sorted(), .sort(), heapq and bisect are not allowed here.")

def ask(rows, rules, timeout=10):
    text = f"{len(rows)}\n" + "".join(f"{n} {a} {s}\n" for n, a, s in rows)
    text += f"{len(rules)}\n" + "".join(f"{f} {d}\n" for f, d in rules)
    return run(text, timeout=timeout)


def model(rows, rules):
    out = list(rows)
    idx = {"name": 0, "age": 1, "score": 2}
    for field, direction in reversed(rules):
        out = sorted(out, key=lambda r: r[idx[field]], reverse=(direction == "desc"))
    return [f"{n} {a} {s}" for n, a, s in out]


ROWS = [("ann", 30, 80), ("bob", 25, 90), ("cy", 30, 70), ("dee", 25, 90), ("eli", 35, 60)]


@pytest.mark.parametrize("rules, why", [
    ([("age", "desc"), ("name", "asc")], "the example: two rules"),
    ([], "no rules: the output equals the input"),
    ([("age", "asc")], "one rule, ties keep input order (bob before dee, ann before cy)"),
    ([("age", "desc")], "descending with ties: still input order, not reversed"),
    ([("score", "desc"), ("age", "asc"), ("name", "desc")], "three rules"),
    ([("name", "desc")], "descending names"),
    ([("age", "asc"), ("age", "desc")], "a repeated field: the second rule never matters"),
])
def test_examples(rules, why):
    got = ask(ROWS, rules)
    assert got == model(ROWS, rules), (
        f"Rules {rules}: expected {model(ROWS, rules)}, got {got} ({why}). "
        "When all rules tie, keep the LEFT record first (stability). Compare ages and scores as ints.")


def test_numbers_not_strings():
    rows = [("a", 9, 100), ("b", 10, 20), ("c", 100, 3)]
    got = ask(rows, [("age", "asc")])
    assert got == model(rows, [("age", "asc")]), "Ages must be compared as integers: 9 < 10 < 100."


def test_random_small():
    rng = random.Random(49)
    fields = ["name", "age", "score"]
    for _ in range(60):
        rows = [("".join(rng.choice("abc") for _ in range(2)), rng.randint(0, 3), rng.randint(0, 3)) for _ in range(rng.randint(1, 10))]
        rules = [(rng.choice(fields), rng.choice(["asc", "desc"])) for _ in range(rng.randint(0, 4))]
        assert ask(rows, rules) == model(rows, rules), f"Rows {rows}, rules {rules}: expected {model(rows, rules)}."


def test_large():
    rng = random.Random(50)
    rows = [("".join(rng.choice("abcd") for _ in range(3)), rng.randint(0, 5), rng.randint(0, 5)) for _ in range(50000)]
    rules = [("age", "desc"), ("name", "asc"), ("score", "desc")]
    assert ask(rows, rules) == model(rows, rules), "50000 records, 3 rules: wrong order or too slow. Use an O(n log n) merge sort."


def test_large_all_ties_keeps_input_order():
    rows = [("x", 1, i) for i in range(50000)]
    assert ask(rows, [("age", "asc"), ("name", "desc")]) == model(rows, [("age", "asc"), ("name", "desc")]), "Everything ties on the rules: the output must equal the input order."
