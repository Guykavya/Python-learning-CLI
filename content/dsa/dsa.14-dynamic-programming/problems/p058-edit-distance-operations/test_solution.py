import ast
import pathlib
import random
import subprocess
import sys

from solution import edit_ops

HERE = pathlib.Path(__file__).parent


def distance(a, b):
    prev = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            cur[j] = prev[j - 1] if a[i - 1] == b[j - 1] else 1 + min(prev[j - 1], prev[j], cur[j - 1])
        prev = cur
    return prev[-1]


def problem_with(a, b, ops):
    """Apply ops to a. Return None if they turn a into b with the fewest operations, else a message."""
    if not isinstance(ops, list):
        return f"return a list of tuples, got {type(ops).__name__}"
    s = a
    for k, op in enumerate(ops):
        if not isinstance(op, tuple) or not op:
            return f"operation {k} is {op!r}; each operation is a tuple like ('delete', 2)"
        kind = op[0]
        if kind == "insert" and len(op) == 3:
            _, p, ch = op
            if not isinstance(ch, str) or len(ch) != 1:
                return f"operation {k} {op!r}: insert one character"
            if not isinstance(p, int) or not 0 <= p <= len(s):
                return (f"operation {k} {op!r}: position {p} is outside 0..{len(s)} for the current string {s!r}. "
                        "Positions refer to the string at that moment")
            s = s[:p] + ch + s[p:]
        elif kind == "delete" and len(op) == 2:
            _, p = op
            if not isinstance(p, int) or not 0 <= p < len(s):
                return (f"operation {k} {op!r}: position {p} is outside 0..{len(s) - 1} for the current string "
                        f"{s!r}")
            s = s[:p] + s[p + 1:]
        elif kind == "replace" and len(op) == 3:
            _, p, ch = op
            if not isinstance(ch, str) or len(ch) != 1:
                return f"operation {k} {op!r}: replace by one character"
            if not isinstance(p, int) or not 0 <= p < len(s):
                return (f"operation {k} {op!r}: position {p} is outside 0..{len(s) - 1} for the current string "
                        f"{s!r}")
            s = s[:p] + ch + s[p + 1:]
        else:
            return f"operation {k} is {op!r}; use ('insert', p, ch), ('delete', p) or ('replace', p, ch)"
    if s != b:
        return (f"your operations turn {a!r} into {s!r}, not {b!r}. If you reversed the list, the positions no "
                "longer match: apply the operations in the order the walk finds them (right to left)")
    want = distance(a, b)
    if len(ops) != want:
        return (f"{len(ops)} operations, but the edit distance is {want}. Is the 'keep' test first, so equal "
                "characters are never replaced?")
    return None


def test_examples():
    for a, b in (("horse", "ros"), ("kitten", "sitting"), ("intention", "execution")):
        msg = problem_with(a, b, edit_ops(a, b))
        assert msg is None, f"a={a!r}, b={b!r}: {msg}."


def test_empty_strings():
    msg = problem_with("", "ab", edit_ops("", "ab"))
    assert msg is None, f"'' -> 'ab' needs two inserts: {msg}."
    msg = problem_with("ab", "", edit_ops("ab", ""))
    assert msg is None, f"'ab' -> '' needs two deletes: {msg}."
    assert edit_ops("", "") == [], "Two empty strings: no operations, []."


def test_equal_strings_need_nothing():
    assert edit_ops("abc", "abc") == [], (
        "Equal strings need no operations. A replace of a character by itself is a wasted operation.")


def test_insert_goes_after_the_prefix():
    msg = problem_with("a", "ab", edit_ops("a", "ab"))
    assert msg is None, f"'a' -> 'ab' is one insert at position 1: {msg}."
    msg = problem_with("ac", "abc", edit_ops("ac", "abc"))
    assert msg is None, f"'ac' -> 'abc' is one insert at position 1: {msg}."


def test_random_validated():
    rng = random.Random(58)
    for _ in range(400):
        a = "".join(rng.choice("abc") for _ in range(rng.randint(0, 8)))
        b = "".join(rng.choice("abc") for _ in range(rng.randint(0, 8)))
        msg = problem_with(a, b, edit_ops(a, b))
        assert msg is None, f"a={a!r}, b={b!r}: {msg}."


def test_big_input_is_fast():
    rng = random.Random(5858)
    a = "".join(rng.choice("abcd") for _ in range(300))
    b = "".join(rng.choice("abcd") for _ in range(280))
    code = (
        "from solution import edit_ops\n"
        f"print(repr(edit_ops({a!r}, {b!r})))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on strings of about 300 characters. A recursion without a memo is exponential: "
        "add a memo, or fill the table and walk back once.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    ops = [tuple(op) for op in ast.literal_eval(r.stdout.strip())]
    msg = problem_with(a, b, ops)
    assert msg is None, f"Large input (about 300 characters each): {msg}."
