import subprocess
import sys
from pathlib import Path

from solution import iter_subsets

HERE = Path(__file__).parent

def run_code(code, timeout, what):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what} took more than {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


def reference_order(items):
    out, path = [], []

    def go(start):
        out.append(path[:])
        for i in range(start, len(items)):
            path.append(items[i])
            go(i + 1)
            path.pop()

    go(0)
    return out


def test_example_order():
    got = list(iter_subsets([1, 2, 3]))
    want = [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
    assert got == want, (
        f"list(iter_subsets([1, 2, 3])) should be {want}, got {got}. "
        "If you only got [[]], the inner call needs `yield from`.")


def test_empty():
    assert list(iter_subsets([])) == [[]], "The empty sequence has one subset, []."


def test_is_an_iterator():
    g = iter_subsets([1, 2])
    assert iter(g) is g, "iter_subsets must return a generator (an iterator), not a list. Use yield."


def test_copies():
    g = iter_subsets(["a", "b", "c"])
    first = next(g)
    second = next(g)
    third = next(g)
    assert (first, second, third) == ([], ["a"], ["a", "b"]), "The first three subsets are [], ['a'], ['a', 'b']."
    second.append("zzz")
    fourth = next(g)
    assert fourth == ["a", "b", "c"], "Changing a list you received must not affect the next subsets: yield path[:] (a copy)."
    assert first == [] and third == ["a", "b"], "Lists already handed out changed later: yield copies, not path itself."


def test_matches_list_version():
    items = list(range(8))
    assert list(iter_subsets(items)) == reference_order(items), "For 8 items the order must match the list version of view 2."


def test_lazy_on_range_40():
    code = ("from solution import iter_subsets\n"
            "it = iter_subsets(range(40))\n"
            "print(next(it), next(it), next(it))\n")
    out = run_code(code, 10, "Taking 3 subsets of range(40) (2^40 subsets in total: do not build them all)")
    assert out == "[] [0] [0, 1]", f"The first three subsets of range(40) are [] [0] [0, 1]; you printed {out!r}."
