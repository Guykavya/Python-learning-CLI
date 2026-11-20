import ast
import itertools
import random
import subprocess
import sys
from pathlib import Path

import pytest

from solution import merge_k_sorted

HERE = Path(__file__).parent
SOLUTION = HERE / "solution.py"


def test_no_shortcuts_in_the_code():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    banned = (names | attrs) & {"sorted", "sort", "merge"}
    assert not banned, (
        f"your file uses {sorted(banned)}. The point of this problem is the loop with a heap that holds one item per "
        "list: write it yourself (heapq.heappush, heappop and heapreplace are allowed).")


def test_the_example():
    got = merge_k_sorted([[1, 4, 5], [1, 3, 4], [2, 6]])
    assert isinstance(got, list), f"return a list, not a {type(got).__name__} (use append, not yield)."
    assert got == [1, 1, 2, 3, 4, 4, 5, 6], f"expected [1, 1, 2, 3, 4, 4, 5, 6], got {got}."


def test_no_lists_and_empty_lists():
    assert merge_k_sorted([]) == [], "no lists at all: the answer is an empty list."
    assert merge_k_sorted([[]]) == [], "one empty list: the answer is an empty list."
    assert merge_k_sorted([[], [], []]) == [], "all lists empty: an empty list."
    assert merge_k_sorted([[], [7], []]) == [7], "empty inner lists must be skipped (lst[0] of [] is an IndexError)."
    assert merge_k_sorted([[3], [], [1, 2]]) == [1, 2, 3], "an empty list in the middle."


def test_one_list_comes_back_as_it_is():
    assert merge_k_sorted([[1, 2, 2, 9]]) == [1, 2, 2, 9], "with one list there is nothing to merge."


def test_the_result_is_a_list():
    got = merge_k_sorted([[1], [2]])
    assert isinstance(got, list), f"return a list, not a {type(got).__name__}."


def test_duplicates_and_negative_numbers():
    got = merge_k_sorted([[-5, -5, 0], [-5, 3], [0, 0, 0]])
    assert got == [-5, -5, -5, 0, 0, 0, 0, 3], (
        f"equal numbers in different lists must all appear: expected [-5, -5, -5, 0, 0, 0, 0, 3], got {got}.")


def test_lists_of_different_lengths():
    got = merge_k_sorted([[1], [2, 3, 4, 5, 6, 7], [0, 10]])
    assert got == [0, 1, 2, 3, 4, 5, 6, 7, 10], (
        f"one list is much longer than the others: after the short ones are used up, the long one must continue. Got {got}.")


def test_floats():
    got = merge_k_sorted([[0.5, 2.5], [0.25, 3.0]])
    assert got == [0.25, 0.5, 2.5, 3.0], f"floats are numbers too, got {got}."


def test_the_input_is_not_changed():
    lists = [[1, 4, 5], [], [1, 3, 4], [2, 6]]
    keep = [list(x) for x in lists]
    merge_k_sorted(lists)
    assert lists == keep, "your function changed the input lists (pop(0)? remove?). Walk with an index instead."


@pytest.mark.parametrize("seed", range(80))
def test_random_inputs(seed):
    rng = random.Random(seed)
    spread = rng.choice([2, 5, 100])
    lists = [sorted(rng.randint(-spread, spread) for _ in range(rng.randint(0, 8))) for _ in range(rng.randint(0, 9))]
    want = sorted(itertools.chain.from_iterable(lists))
    got = merge_k_sorted(lists)
    assert got == want, f"lists = {lists}\nexpected {want}\ngot      {got}"


BIG = """
import itertools, random
from solution import merge_k_sorted
rng = random.Random(3)
lists = [sorted(rng.randint(0, 10**6) for _ in range(200)) for _ in range(2000)]
out = merge_k_sorted(lists)
print("OK" if out == sorted(itertools.chain.from_iterable(lists)) else "WRONG", len(out))
"""


def test_two_thousand_lists_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG], cwd=HERE, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        pytest.fail(
            "2,000 lists of 200 numbers did not finish in 10 seconds. Merging the lists one after the other, or "
            "scanning all front items for every output number, costs O(N * k). Use a heap with one item per list: "
            "O(N log k).")
    assert r.returncode == 0, "your code crashed on the big case:\n" + r.stderr[-600:]
    assert r.stdout.strip() == "OK 400000", f"big case: expected 'OK 400000', got {r.stdout.strip()!r}."
