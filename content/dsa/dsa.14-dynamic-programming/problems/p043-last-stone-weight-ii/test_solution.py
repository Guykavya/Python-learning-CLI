import pathlib
import random
import subprocess
import sys
from functools import cache

from solution import last_stone_weight_ii

HERE = pathlib.Path(__file__).parent


@cache
def play(stones):
    """Play the game every possible way. stones is a sorted tuple. Only for a few stones."""
    if len(stones) <= 1:
        return stones[0] if stones else 0
    best = None
    n = len(stones)
    for i in range(n):
        for j in range(i + 1, n):
            x, y = stones[i], stones[j]          # sorted, so x <= y
            rest = list(stones[:i] + stones[i + 1:j] + stones[j + 1:])
            if y > x:
                rest.append(y - x)
            got = play(tuple(sorted(rest)))
            if best is None or got < best:
                best = got
    return best


def heaviest_two_game(stones):
    """The greedy rule of 'Last stone weight I' (not optimal here)."""
    s = sorted(stones)
    while len(s) > 1:
        y = s.pop()
        x = s.pop()
        if y > x:
            s.append(y - x)
            s.sort()
    return s[0] if s else 0


def closest_split(stones):
    total = sum(stones)
    sums = {0}
    for x in stones:
        sums |= {s + x for s in sums}
    return min(abs(total - 2 * s) for s in sums)


def test_examples():
    assert last_stone_weight_ii([2, 7, 4, 1, 8, 1]) == 1, (
        "Expected 1: the groups {2, 8, 1} and {7, 4, 1} sum to 11 and 12.")
    assert last_stone_weight_ii([31, 26, 33, 21, 40]) == 5, (
        "Expected 5: the groups {26, 31, 21} = 78 and {33, 40} = 73 differ by 5. "
        "Smashing the two heaviest each time leaves 9; the game is not won greedily.")


def test_small_cases():
    assert last_stone_weight_ii([5]) == 5, "One stone: nothing to smash, it is the last stone."
    assert last_stone_weight_ii([3, 3]) == 0, "Equal stones destroy each other: 0."
    assert last_stone_weight_ii([1, 6]) == 5, (
        "[1, 6] leaves 5. If you got 1, a stone was used twice (s loop upwards).")
    assert last_stone_weight_ii([1, 1, 4, 2, 2]) == 0, "{4, 1} and {1, 2, 2} both sum to 5, so nothing is left: 0."


def test_greedy_game_is_wrong():
    stones = [31, 26, 33, 21, 40]
    assert heaviest_two_game(stones) == 9
    assert last_stone_weight_ii(list(stones)) == 5, (
        "Smashing the two heaviest stones each time gives 9 here, but 5 is reachable. "
        "Reduce the game to splitting the stones into two groups with sums as close as possible.")


def test_random_against_playing_every_game():
    rng = random.Random(43)
    for _ in range(150):
        stones = [rng.randint(1, 12) for _ in range(rng.randint(1, 6))]
        want = play(tuple(sorted(stones)))
        got = last_stone_weight_ii(list(stones))
        assert got == want, (
            f"stones={stones}: expected {want} (found by playing every game), got {got}. "
            "Take the largest reachable subset sum s <= total // 2 and return total - 2 * s.")


def test_big_input_is_fast():
    rng = random.Random(4343)
    cases = [[rng.randint(1, 100) for _ in range(100)], [2] * 99 + [1], [100] * 50 + [99] * 50]
    want = [closest_split(c) for c in cases]
    code = (
        "from solution import last_stone_weight_ii\n"
        f"cases = {cases!r}\n"
        "print(*[last_stone_weight_ii(c) for c in cases])\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 100 stones. Trying every split or every game is exponential: add a memo, "
        "or fill the subset-sum table up to total // 2.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == [str(w) for w in want], (
        f"Large inputs: expected {want}, got {r.stdout.split()}.")
