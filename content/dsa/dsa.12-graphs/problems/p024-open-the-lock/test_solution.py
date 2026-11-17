import random
from collections import deque
from itertools import product

from solution import open_lock


def model(deadends, target):
    k = len(target)
    dead = set(deadends)
    start = "0" * k
    if start in dead:
        return -1
    states = ["".join(p) for p in product("0123456789", repeat=k)]
    dist = {start: 0}
    queue = deque([start])
    while queue:
        s = queue.popleft()
        for t in states:
            if t in dist or t in dead:
                continue
            diffs = [i for i in range(k) if s[i] != t[i]]
            if len(diffs) == 1 and (int(s[diffs[0]]) - int(t[diffs[0]])) % 10 in (1, 9):
                dist[t] = dist[s] + 1
                queue.append(t)
    return dist.get(target, -1)


def test_the_examples():
    assert open_lock(["0201", "0101", "0102", "1212", "2002"], "0202") == 6, "The chapter's example: 6 moves around the dead ends."
    assert open_lock(["8888"], "0009") == 1, "0009 is ONE move: the last wheel turns down from 0 to 9 (wrap around with % 10)."
    assert open_lock(["9", "1"], "5") == -1, "One wheel: both neighbours of 0 are dead, so 5 cannot be reached."
    assert open_lock([], "55") == 10, "Two wheels, no dead ends: 5 + 5 moves. Use k = len(target), not 4."


def test_start_and_target_rules():
    assert open_lock(["0000"], "1234") == -1, "The start 0000 is dead: the lock is jammed from the beginning, -1."
    assert open_lock(["000"], "000") == -1, "The start is dead: -1 even when target is the start."
    assert open_lock([], "0000") == 0, "target is the start: 0 moves."
    assert open_lock(["0001"], "0001") == -1, "The target itself is dead: -1."


def test_wrap_around_both_ways():
    assert open_lock([], "9") == 1, "0 down is 9: one move."
    assert open_lock(["9"], "8") == 8, "With 9 dead, the wheel must go up 0 -> 1 -> ... -> 8: 8 moves."
    assert open_lock([], "999") == 3, "Each wheel goes down once: 3 moves."


def test_random_small_locks():
    rng = random.Random(1224)
    for _ in range(120):
        k = rng.randint(1, 2)
        dead = sorted({"".join(rng.choice("0123456789") for _ in range(k)) for _ in range(rng.randint(0, 6 * k))})
        target = "".join(rng.choice("0123456789") for _ in range(k))
        want = model(dead, target)
        got = open_lock(dead, target)
        assert got == want, f"open_lock({dead}, {target!r}) should be {want}, got {got}."


def test_five_wheels():
    got = open_lock([], "55555")
    assert got == 25, f"Five wheels, no dead ends: 5 * 5 = 25 moves; got {got}."
    dead = ["1" + "0" * 4, "9" + "0" * 4]
    got = open_lock(dead, "50000")
    assert got == 7, (
        f"With 10000 and 90000 dead, the first wheel cannot turn from 00000 directly; turning another wheel away and back "
        f"costs 2 extra moves: 5 + 2 = 7. Got {got}.")
