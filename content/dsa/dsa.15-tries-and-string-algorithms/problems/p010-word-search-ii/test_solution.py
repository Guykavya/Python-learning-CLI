import pathlib
import random
import subprocess
import sys

from solution import find_words

HERE = pathlib.Path(__file__).parent


def can_trace(board, word):
    """Slow, obviously right: one DFS per start cell (small boards only)."""
    rows, cols = len(board), len(board[0])

    def go(r, c, k, used):
        if board[r][c] != word[k] or (r, c) in used:
            return False
        if k == len(word) - 1:
            return True
        used = used | {(r, c)}
        return any(0 <= r + dr < rows and 0 <= c + dc < cols and go(r + dr, c + dc, k + 1, used)
                   for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))

    return any(go(r, c, 0, frozenset()) for r in range(rows) for c in range(cols))


def test_chapter_example():
    board = [list("oaan"), list("etae"), list("ihkr"), list("iflv")]
    copy = [row[:] for row in board]
    got = find_words(board, ["oath", "pea", "eat", "rain"])
    assert got == ["eat", "oath"], f"Expected ['eat', 'oath'], got {got}."
    assert board == copy, "The board must be unchanged when find_words returns: restore every cell you mark."


def test_no_cell_reuse():
    got = find_words([list("ab")], ["ab", "ba", "aba"])
    assert got == ["ab", "ba"], (
        f"Expected ['ab', 'ba'], got {got}. 'aba' would use the cell 'a' twice in one word.")


def test_report_once():
    board = [list("aa"), list("aa")]
    got = find_words(board, ["aa", "aa", "aaa"])
    assert got == ["aa", "aaa"], f"Each word once, sorted: expected ['aa', 'aaa'], got {got}."
    assert find_words([list("a")], ["a", "b"]) == ["a"]


def test_word_longer_than_board():
    assert find_words([list("ab"), list("cd")], ["abdca", "abdc"]) == ["abdc"], (
        "'abdc' walks all 4 cells; 'abdca' would need a fifth.")


def test_random_against_slow():
    rng = random.Random(1510)
    for _ in range(80):
        rows, cols = rng.randint(1, 4), rng.randint(1, 4)
        board = [[rng.choice("abc") for _ in range(cols)] for _ in range(rows)]
        words = ["".join(rng.choice("abc") for _ in range(rng.randint(1, 5))) for _ in range(rng.randint(1, 12))]
        want = sorted({w for w in words if can_trace(board, w)})
        copy = [row[:] for row in board]
        got = find_words(board, list(words))
        assert got == want, f"board={copy}, words={words}: expected {want}, got {got}."
        assert board == copy, "The board must be restored after the search."


def test_big_board_needs_a_trie():
    code = (
        "from solution import find_words\n"
        "board = [['a'] * 12 for _ in range(12)]\n"
        "spots = [(11, c) for c in range(0, 12, 2)] + [(0, c) for c in range(1, 12, 2)]\n"
        "for ch, (r, c) in zip('bcdefghijklm', spots):\n"
        "    board[r][c] = ch\n"
        "words = ['a' * k + x for k in range(1, 8) for x in 'bcd']\n"
        "words += ['a' * k + x + y for k in range(5, 9) for x in 'bcdefg' for y in 'hijklm']\n"
        "print(len(find_words(board, words)))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on a 12 by 12 board of 'a's. Searching each word separately re-explores the same "
        "a-paths for every word that cannot be traced. Put the words in a trie, search all of them at once, "
        "and delete trie branches that hold no more words.")
    assert r.returncode == 0, "Your code crashed on the big board:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["21"], f"Big board: expected 21 words found, got {r.stdout.split()}."
