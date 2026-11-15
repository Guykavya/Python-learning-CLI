import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent

SETUP = """
from solution import has_cycle

class SNode:
    __slots__ = ("val", "next")
    __hash__ = None
    def __init__(self, val, next=None):
        self.val = val
        self.next = next

def make(n, loop_to):
    ns = [SNode(i + 1) for i in range(n)]
    for a, b in zip(ns, ns[1:]):
        a.next = b
    if n and loop_to is not None:
        ns[-1].next = ns[loop_to]
    return ns[0] if ns else None
"""


def check(n, loop_to):
    """Run has_cycle(make(n, loop_to)) in its own process, with a time limit."""
    code = SETUP + f"print(has_cycle(make({n}, {loop_to})))\n"
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=5)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    if r.returncode != 0:
        if "unhashable" in r.stderr:
            return "SET"
        return "CRASH: " + r.stderr[-600:]
    return r.stdout.strip()


def describe(n, loop_to):
    vals = " -> ".join(str(i + 1) for i in range(n)) or "(empty)"
    return vals + (f" with {n}.next pointing back to {loop_to + 1}" if n and loop_to is not None else " -> None")


@pytest.mark.parametrize("n, loop_to", [
    (3, 1),          # the bug report: 3 -> 2
    (2, 1),          # node 2 points to itself
    (5, 3),
    (6, 2),
    (10, 7),
])
def test_cycle_not_through_head(n, loop_to):
    got = check(n, loop_to)
    assert got != "TIMEOUT", (
        f"has_cycle on {describe(n, loop_to)} did not finish in 5 seconds. The cycle does not include the head, "
        "so fast never comes back to the head. Compare fast with slow instead: inside the cycle they must meet.")
    assert got != "SET", "Do not put nodes into a set: fix the comparison and keep O(1) memory."
    assert got == "True", f"{describe(n, loop_to)} has a cycle: expected True, got {got}."


@pytest.mark.parametrize("n, loop_to, want", [
    (0, None, "False"),
    (1, None, "False"),
    (3, None, "False"),
    (4, None, "False"),
    (1, 0, "True"),
    (3, 0, "True"),
    (4, 0, "True"),
])
def test_old_cases_still_work(n, loop_to, want):
    got = check(n, loop_to)
    assert got != "TIMEOUT", f"has_cycle on {describe(n, loop_to)} did not finish in 5 seconds."
    assert got == want, (
        f"has_cycle on {describe(n, loop_to)} should be {want}, got {got}. "
        "If every list is True now, you compare slow and fast before moving them (both start on the head).")


def test_long_cycle_in_the_middle():
    got = check(100_000, 40_000)
    assert got == "True", (
        f"100,000 nodes with the last pointing back to node 40,001: expected True, got {got}.")
