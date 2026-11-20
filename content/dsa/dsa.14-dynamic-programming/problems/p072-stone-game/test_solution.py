import pathlib
import random
import subprocess
import sys

from solution import stone_game

HERE = pathlib.Path(__file__).parent


def brute(piles):
    """Plain minimax over every sequence of moves: 2^n, tiny inputs only."""
    if not piles:
        return 0
    return max(piles[0] - brute(piles[1:]), piles[-1] - brute(piles[:-1]))


def test_examples():
    assert stone_game([3, 9, 1, 2]) == 7, "Expected 7: the first player takes 2, then always gets the 9 (11 - 4)."
    assert stone_game([5, 3, 4, 5]) == 1, "Expected 1."
    assert stone_game([2, 7, 3]) == -2, (
        "Expected -2: whatever the first player takes, the second takes 7. A negative answer is fine.")


def test_small_rows():
    assert stone_game([]) == 0, "No piles: difference 0."
    assert stone_game([7]) == 7, "One pile: the first player takes it. Base case f(i, i) = piles[i]."
    assert stone_game([4, 9]) == 5, "Two piles: take 9, the other gets 4."


def test_greedy_is_not_enough():
    assert stone_game([4, 1, 4, 7, 5]) == 3, (
        "Expected 3. Taking the larger end (5) lets the second player take 7 and gives -1. "
        "Compare BOTH moves: max(piles[i] - f(i+1, j), piles[j] - f(i, j-1)).")


def test_random_against_minimax():
    rng = random.Random(72)
    for _ in range(400):
        piles = [rng.randint(1, 20) for _ in range(rng.randint(0, 10))]
        want = brute(piles)
        got = stone_game(list(piles))
        assert got == want, (
            f"piles={piles}: expected {want} (every line of play tried), got {got}. The opponent's best "
            "difference on the smaller range is SUBTRACTED: piles[i] - f(i+1, j).")


def test_large_input_in_time():
    rng = random.Random(7200)
    piles = [rng.randint(1, 1000) for _ in range(500)]
    code = (
        "import sys\n"
        "from solution import stone_game\n"
        "piles = [int(x) for x in sys.stdin.read().split()]\n"
        "print(stone_game(piles), stone_game([5] * 500), stone_game([5] * 501))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, input=" ".join(map(str, piles)),
                           capture_output=True, text=True, timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 500 piles. Trying both moves at every turn without a memo is exponential: "
        "add a memo on (i, j), or fill the table by length.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["12740", "0", "5"], (
        "Expected 12740 for the random row, 0 for 500 equal piles (each player gets 250) and 5 for 501 equal "
        f"piles; got {r.stdout.split()}.")
