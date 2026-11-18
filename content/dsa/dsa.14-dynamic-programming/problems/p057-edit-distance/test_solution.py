import pathlib
import random
import subprocess
import sys

from solution import edit_distance

HERE = pathlib.Path(__file__).parent


def plain_recursion(a, b):
    """The definition, with no memo (only for short strings)."""
    if not a:
        return len(b)
    if not b:
        return len(a)
    if a[-1] == b[-1]:
        return plain_recursion(a[:-1], b[:-1])
    return 1 + min(plain_recursion(a[:-1], b[:-1]), plain_recursion(a[:-1], b), plain_recursion(a, b[:-1]))


def table(a, b):
    prev = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            cur[j] = prev[j - 1] if a[i - 1] == b[j - 1] else 1 + min(prev[j - 1], prev[j], cur[j - 1])
        prev = cur
    return prev[-1]


def test_chapter_examples():
    assert edit_distance("horse", "ros") == 3, "Expected 3: horse -> rorse -> rose -> ros."
    assert edit_distance("kitten", "sitting") == 3, "Expected 3: replace k, replace e, insert g."
    assert edit_distance("intention", "execution") == 5, "Expected 5."


def test_empty_strings():
    assert edit_distance("", "abc") == 3, "From '' to 'abc': 3 inserts. f[0][j] = j, not 0."
    assert edit_distance("abc", "") == 3, "From 'abc' to '': 3 deletes. f[i][0] = i, not 0."
    assert edit_distance("", "") == 0, "Two empty strings: 0."


def test_equal_strings_cost_nothing():
    assert edit_distance("abc", "abc") == 0, (
        "Equal strings: 0. If you got more, equal characters are charged 1: copy the diagonal without + 1.")
    assert edit_distance("a", "a") == 0, "Equal: 0."


def test_one_operation_each():
    assert edit_distance("cat", "cut") == 1, "One replace."
    assert edit_distance("cat", "cart") == 1, "One insert."
    assert edit_distance("cart", "cat") == 1, "One delete."
    assert edit_distance("abc", "bca") == 2, (
        "Every position differs, but delete 'a' and insert 'a' at the end is 2. Count operations, not positions.")


def test_random_against_plain_recursion():
    rng = random.Random(57)
    for _ in range(300):
        a = "".join(rng.choice("abc") for _ in range(rng.randint(0, 6)))
        b = "".join(rng.choice("abc") for _ in range(rng.randint(0, 6)))
        want = plain_recursion(a, b)
        got = edit_distance(a, b)
        assert got == want, (
            f"a={a!r}, b={b!r}: expected {want} (from the recursive definition), got {got}. "
            "Check the base row/column (0, 1, 2, ...) and the equal case (diagonal, no + 1).")


def test_big_input_is_fast():
    rng = random.Random(5757)
    a = "".join(rng.choice("abcd") for _ in range(400))
    b = "".join(rng.choice("abcd") for _ in range(380))
    want = [table(a, b), 400, 200]
    code = (
        "from solution import edit_distance\n"
        f"print(edit_distance({a!r}, {b!r}), edit_distance('x' * 400, 'y' * 400), "
        "edit_distance('ab' * 200, 'b' * 200))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on two strings of about 400 characters. Without a memo every mismatch makes three "
        "calls: exponential: add a memo, or fill the table.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == [str(w) for w in want], (
        f"Large inputs: expected {want}, got {r.stdout.split()}.")
