import random
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

from solution import least_interval

HERE = Path(__file__).parent


def brute(tasks, n):
    """The least number of time units, found by a breadth-first search over every state.
    A state is (copies left of each kind, units each kind still has to wait). Tiny inputs only."""
    kinds = sorted(set(tasks))
    counts = tuple(tasks.count(k) for k in kinds)
    m = len(kinds)
    if sum(counts) == 0:
        return 0
    start = (counts, (0,) * m)
    frontier, seen, t = {start}, {start}, 0
    while frontier:
        t += 1
        nxt = set()
        for counts, waits in frontier:
            base = tuple(max(w - 1, 0) for w in waits)
            options = [(counts, base)]                                # stay idle
            for i in range(m):
                if counts[i] > 0 and waits[i] == 0:                   # run kind i now
                    c = list(counts)
                    c[i] -= 1
                    w = list(base)
                    w[i] = n
                    options.append((tuple(c), tuple(w)))
            for state in options:
                if sum(state[0]) == 0:
                    return t
                if state not in seen:
                    seen.add(state)
                    nxt.add(state)
        frontier = nxt


def formula(tasks, n):
    """The known closed form (used only for big inputs; the tests check it against brute() for small ones)."""
    if not tasks:
        return 0
    counts = Counter(tasks).values()
    m = max(counts)
    k = sum(1 for c in counts if c == m)
    return max(len(tasks), (m - 1) * (n + 1) + k)


def test_the_examples():
    assert least_interval(list("AAABBB"), 2) == 8, "A B _ A B _ A B: eight units."
    assert least_interval(list("AAABBB"), 0) == 6, "no cooldown: one unit per task."
    assert least_interval(list("AAAAAABCDEFG"), 2) == 16, "six A's need 5 gaps of 3 units plus the last A: 16; the other tasks fill idle units."


def test_no_tasks_and_one_task():
    assert least_interval([], 3) == 0, "no tasks: 0 units."
    assert least_interval(["A"], 5) == 1, "one task: the cooldown does not matter, 1 unit."


def test_cooldown_is_between_equal_tasks_only():
    assert least_interval(list("ABC"), 10) == 3, "three different tasks never wait for each other."
    assert least_interval(list("AAA"), 2) == 7, "A _ _ A _ _ A: seven units."
    assert least_interval(list("AAA"), 0) == 3, "n = 0: three units."


def test_two_kinds_with_the_same_maximum_count():
    assert least_interval(list("AABB"), 3) == 6, "A B _ _ A B: six units (the last block holds A and B)."
    assert least_interval(list("AAABBBCC"), 2) == 8, "A B C A B C A B: eight units, no idle unit."


def test_no_idle_unit_needed():
    assert least_interval(list("AABBCCDD"), 1) == 8, "there are enough different tasks: the answer is the number of tasks."
    assert least_interval(list("AAABBBCCCDDD"), 2) == 12, "every unit can run a task."


def test_names_can_be_words():
    tasks = ["write", "write", "test", "test", "deploy"]
    assert least_interval(tasks, 2) == brute(tasks, 2), "task names can be any strings; equal names are the same kind."


def test_the_input_is_not_changed():
    tasks = list("AAABBC")
    least_interval(tasks, 2)
    assert tasks == list("AAABBC"), "your function changed the list of tasks."


@pytest.mark.parametrize("seed", range(80))
def test_small_random_inputs_against_the_search(seed):
    rng = random.Random(seed)
    kinds = "ABCD"[:rng.randint(1, 4)]
    tasks = [rng.choice(kinds) for _ in range(rng.randint(0, 9))]
    n = rng.randint(0, 4)
    want = brute(tasks, n)
    got = least_interval(list(tasks), n)
    assert got == want, (
        f"tasks = {''.join(tasks)}, n = {n}: the best schedule needs {want} units, you returned {got}. "
        "Check: a task run at time t is available again at t + n + 1; idle units count; run the task with the most copies left.")


BIG = """
import random
from collections import Counter
from solution import least_interval

def formula(tasks, n):
    counts = Counter(tasks).values()
    m = max(counts)
    k = sum(1 for c in counts if c == m)
    return max(len(tasks), (m - 1) * (n + 1) + k)

rng = random.Random(21)
cases = [
    (["A"] * 30000 + ["B"] * 30000, 20),
    ([rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(100000)], 50),
    ([rng.choice("ABC") for _ in range(100000)], 2),
    (["A"] * 20000 + ["B"] * 20000 + ["C"] * 5000, 100),
    ([chr(65 + i % 26) for i in range(100000)], 25),
]
print(" ".join("OK" if least_interval(list(t), n) == formula(t, n) else "WRONG" for t, n in cases))
"""


def test_big_inputs_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG], cwd=HERE, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        pytest.fail(
            "the big cases (up to 100,000 tasks) did not finish in 10 seconds. One heap operation per time unit is "
            "enough; do not search the schedule or rebuild the heap from scratch in every unit.")
    assert r.returncode == 0, "your code crashed on the big case:\n" + r.stderr[-600:]
    assert r.stdout.split() == ["OK"] * 5, f"big cases gave {r.stdout.strip()!r}; every case must be OK."
