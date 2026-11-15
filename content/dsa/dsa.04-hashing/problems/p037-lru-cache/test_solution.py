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


def ask(c, cmds, timeout=10):
    return run(f"{c}\n{len(cmds)}\n" + "\n".join(cmds) + "\n", timeout=timeout)


def model(c, cmds):
    cache, out = {}, []
    for cmd in cmds:
        p = cmd.split()
        k = int(p[1])
        if p[0] == "get":
            if k in cache:
                cache[k] = cache.pop(k)
                out.append(str(cache[k]))
            else:
                out.append("-1")
        else:
            if k in cache:
                del cache[k]
            elif len(cache) == c:
                del cache[next(iter(cache))]
            cache[k] = int(p[2])
    return out


def test_example():
    cmds = ["put 1 1", "put 2 2", "get 1", "put 3 3", "get 2", "put 4 4", "get 1", "get 3", "get 4"]
    assert ask(2, cmds) == ["1", "-1", "-1", "3", "4"], (
        "Expected 1 -1 -1 3 4. Hint: after get 1, key 2 is the least recently used; put 3 3 evicts 2.")


def test_get_refreshes():
    cmds = ["put 1 10", "put 2 20", "get 1", "put 3 30", "get 1", "get 2"]
    assert ask(2, cmds) == ["10", "10", "-1"], (
        "get must mark the key as recently used: after get 1, the key evicted by put 3 is 2, not 1.")


def test_update_does_not_evict_and_refreshes():
    cmds = ["put 1 1", "put 2 2", "put 1 100", "get 2", "put 3 3", "get 1", "get 2", "get 3"]
    assert ask(2, cmds) == ["2", "-1", "2", "3"], (
        "Updating key 1 must not evict anything and must refresh it; then get 2 refreshes 2, so put 3 evicts 1.")


def test_capacity_one():
    cmds = ["put 1 1", "put 2 2", "get 1", "get 2", "put 2 5", "get 2"]
    assert ask(1, cmds) == ["-1", "2", "5"], "With capacity 1 every new key evicts the previous one."


def test_missing_key():
    assert ask(3, ["get 7"]) == ["-1"], "A key that was never stored gives -1."


def test_random_small():
    rng = random.Random(42)
    for _ in range(40):
        c = rng.randint(1, 4)
        cmds = []
        for _ in range(rng.randint(1, 25)):
            if rng.random() < 0.5:
                cmds.append(f"get {rng.randint(0, 6)}")
            else:
                cmds.append(f"put {rng.randint(0, 6)} {rng.randint(0, 99)}")
        want = model(c, cmds)
        got = ask(c, cmds)
        assert got == want, f"c={c}, commands {cmds}: expected {want}, got {got}."


def test_large():
    rng = random.Random(43)
    c = 50000
    cmds = []
    for _ in range(200000):
        k = rng.randint(0, 80000)
        cmds.append(f"get {k}" if rng.random() < 0.5 else f"put {k} {rng.randint(0, 10**9)}")
    assert ask(c, cmds) == model(c, cmds), (
        "200000 commands with capacity 50000. Tracking recency with a list (remove, append) is O(c) per command; "
        "pop and reinsert in a dict instead.")
