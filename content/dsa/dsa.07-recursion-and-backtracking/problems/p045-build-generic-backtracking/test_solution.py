import ast
import itertools
from pathlib import Path

from solution import backtrack, permutations, subsets

SOLUTION = Path(__file__).with_name("solution.py")


def test_example_two_letters():
    got = backtrack(lambda p: "ab" if len(p) < 2 else "", lambda p, o: True, lambda p: len(p) == 2)
    assert got == [["a", "a"], ["a", "b"], ["b", "a"], ["b", "b"]], (
        f"The example should give [['a','a'], ['a','b'], ['b','a'], ['b','b']] in this order, got {got}. "
        "If all answers are [], you recorded path instead of path[:].")


def test_problem_1_binary_strings_without_11():
    got = backtrack(lambda p: ["0", "1"] if len(p) < 4 else [],
                    lambda p, o: not (o == "1" and p and p[-1] == "1"),
                    lambda p: len(p) == 4)
    got = ["".join(p) for p in got]
    want = ["0000", "0001", "0010", "0100", "0101", "1000", "1001", "1010"]
    assert got == want, (
        f"Strings of length 4 with no '11', in depth-first order, should be {want}, got {got}. "
        "Check that invalid options are skipped and that options are tried in the order choices() gives.")


def test_problem_2_six_queens():
    n = 6

    def safe(path, c):
        r = len(path)
        return all(c != pc and abs(r - pr) != abs(c - pc) for pr, pc in enumerate(path))

    got = backtrack(lambda p: range(n) if len(p) < n else [], safe, lambda p: len(p) == n)
    assert got == [[1, 3, 5, 0, 2, 4], [2, 5, 1, 4, 0, 3], [3, 0, 4, 1, 5, 2], [4, 2, 0, 5, 3, 1]], (
        f"6-queens through your engine should find the 4 solutions in column order, got {got}.")


def test_problem_3_combination_sum():
    cands = [2, 3, 6, 7]
    got = backtrack(lambda p: [c for c in cands if not p or c >= p[-1]] if sum(p) < 7 else [],
                    lambda p, c: sum(p) + c <= 7,
                    lambda p: sum(p) == 7)
    assert got == [[2, 2, 3], [7]], f"Combination sum [2, 3, 6, 7] -> 7 through your engine should give [[2, 2, 3], [7]], got {got}."


def test_records_and_keeps_going():
    got = backtrack(lambda p: [x for x in (1, 2, 3) if not p or x > p[-1]], lambda p, o: True, lambda p: True)
    assert got == [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]], (
        f"When is_done is always True, every node is recorded and the search continues below it; got {got}. "
        "Do not return right after recording.")


def test_callbacks_never_see_invalid_paths():
    seen_bad = []

    def choices(p):
        if "x" in p:
            seen_bad.append(list(p))
        return "xy" if len(p) < 3 else ""

    def is_done(p):
        if "x" in p:
            seen_bad.append(list(p))
        return len(p) == 3

    got = backtrack(choices, lambda p, o: o != "x", is_done)
    assert got == [["y", "y", "y"]], f"Only 'yyy' is valid, got {got}."
    assert not seen_bad, f"Your engine called choices/is_done with paths containing an invalid option: {seen_bad[:3]}. Check is_valid BEFORE appending."


def test_records_are_copies():
    got = backtrack(lambda p: [1] if len(p) < 2 else [], lambda p, o: True, lambda p: True)
    assert got == [[], [1], [1, 1]], "Each recorded answer must be a copy of the path at that moment."
    got[0].append(99)
    assert got[1] == [1], "The recorded answers share one list: append path[:], not path."


def test_subsets():
    got = sorted(subsets([1, 2, 3]))
    assert got == [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]], f"subsets([1, 2, 3]) has 8 subsets, got {got}."
    assert subsets([]) == [[]], "subsets([]) is [[]]."
    assert len(subsets(list(range(10)))) == 1024, "10 items have 1024 subsets."


def test_permutations():
    got = sorted(permutations([1, 2, 3]))
    assert got == sorted(list(p) for p in itertools.permutations([1, 2, 3])), f"permutations([1, 2, 3]) should have 6 orderings, got {got}."
    assert sorted(permutations(["b", "a"])) == [["a", "b"], ["b", "a"]], "Items can be any values."
    assert len(permutations(list(range(6)))) == 720, "6 items have 720 orderings."


def test_users_call_the_engine():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    funcs = {f.name: f for f in tree.body if isinstance(f, ast.FunctionDef)}
    for name in ("subsets", "permutations"):
        assert name in funcs, f"Define {name} at the top level of solution.py."
        calls = {n.func.id for n in ast.walk(funcs[name]) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        assert "backtrack" in calls, f"{name} must use your backtrack engine (call backtrack inside it)."
