import copy
import random

import pytest

from solution import exist

BOARD = ["ABCE", "SFCS", "ADEE"]


def brute(rows, word):
    R, C = len(rows), len(rows[0])

    def go(r, c, k, seen):
        if rows[r][c] != word[k]:
            return False
        if k == len(word) - 1:
            return True
        seen = seen | {(r, c)}
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and (nr, nc) not in seen and go(nr, nc, k + 1, seen):
                return True
        return False

    return any(go(r, c, 0, frozenset()) for r in range(R) for c in range(C))


def check(rows, word, want, why):
    board = [list(r) for r in rows]
    before = copy.deepcopy(board)
    got = exist(board, word)
    assert got is want, f"exist({rows}, {word!r}) should be {want}: {why}."
    assert board == before, (
        f"After exist(..., {word!r}) the board is {board}, but it must be unchanged. "
        "You forgot to un-mark: restore the letter after the recursive calls, also when the word was found.")


@pytest.mark.parametrize("word, want, why", [
    ("ABCCED", True, "A B C, then the C below, then E and D"),
    ("SEE", True, "S E E on the right side"),
    ("ABCB", False, "the B cell cannot be used twice"),
    ("A", True, "a one-letter word"),
    ("Z", False, "a letter that is not on the board"),
    ("ABCESEEDAS", True, "a long path around the board"),
    ("ASADB", False, "A S A then D, but no B next to D"),
])
def test_example_board(word, want, why):
    check(BOARD, word, want, why)


def test_single_cell():
    check(["a"], "a", True, "a 1x1 board with the word")
    check(["a"], "aa", False, "the single cell cannot be used twice")


def test_no_reuse_on_all_same_letter():
    check(["AA", "AA"], "AAAA", True, "four different A cells")
    check(["AA", "AA"], "AAAAA", False, "only four cells, five letters needed: some cell would be used twice")


def test_case_matters():
    check(["aB"], "ab", False, "upper and lower case are different letters")


def test_last_letter_in_corner():
    check(["XY", "QZ"], "XYZ", True, "the word ends on the bottom-right corner")


def test_random_against_brute_force():
    rng = random.Random(31)
    for _ in range(150):
        R, C = rng.randint(1, 4), rng.randint(1, 4)
        rows = ["".join(rng.choice("AB") for _ in range(C)) for _ in range(R)]
        word = "".join(rng.choice("AB") for _ in range(rng.randint(1, 7)))
        check(rows, word, brute(rows, word), "compared with a brute-force search")
