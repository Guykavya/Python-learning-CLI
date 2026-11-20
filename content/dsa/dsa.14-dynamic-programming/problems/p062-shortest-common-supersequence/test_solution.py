import pathlib
import random
import subprocess
import sys

from solution import shortest_supersequence

HERE = pathlib.Path(__file__).parent


def is_subsequence(small, big):
    it = iter(big)
    return all(ch in it for ch in small)


def lcs_length(a, b):
    f = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                f[i][j] = f[i - 1][j - 1] + 1
            else:
                f[i][j] = max(f[i - 1][j], f[i][j - 1])
    return f[-1][-1]


def check(a, b, got):
    """Validate an answer: a string, contains a and b in order, shortest length."""
    assert isinstance(got, str), f"a={a!r}, b={b!r}: return a string, got {type(got).__name__}."
    assert is_subsequence(a, got), (
        f"a={a!r}, b={b!r}: your answer {got!r} does not contain a={a!r} as a subsequence. Every letter must be "
        "written: on a step up write a[i-1], and copy the leftovers when one index reaches 0.")
    assert is_subsequence(b, got), (
        f"a={a!r}, b={b!r}: your answer {got!r} does not contain b={b!r} as a subsequence. Write b[j-1] on a "
        "step left, copy what is left of b at the end, and reverse the collected letters.")
    want = len(a) + len(b) - lcs_length(a, b)
    assert len(got) == want, (
        f"a={a!r}, b={b!r}: your answer {got!r} is valid but has length {len(got)}; the shortest has length "
        f"{want} = len(a) + len(b) - LCS. Share the letters of the LCS (diagonal steps) and follow the LARGER "
        "neighbour in the table.")


def test_examples():
    check("abac", "cab", shortest_supersequence("abac", "cab"))
    assert len(shortest_supersequence("abac", "cab")) == 5, "abac and cab share 'ab': length 4 + 3 - 2 = 5."


def test_empty_and_equal():
    assert shortest_supersequence("", "") == "", "Two empty strings: the answer is ''."
    assert shortest_supersequence("abc", "") == "abc", (
        "b is empty: the answer is a itself. Did you forget to copy the letters left in a after the loop?")
    assert shortest_supersequence("", "xyz") == "xyz", "a is empty: the answer is b. Copy the leftovers of b."
    assert shortest_supersequence("abc", "abc") == "abc", "Equal strings share every letter: the answer is the string."


def test_nothing_shared():
    got = shortest_supersequence("ab", "cd")
    check("ab", "cd", got)
    assert len(got) == 4, "No common letters: every letter appears once, length 4."


def test_one_inside_the_other():
    check("ace", "abcde", shortest_supersequence("ace", "abcde"))
    assert shortest_supersequence("ace", "abcde") == "abcde", "'ace' is already a subsequence of 'abcde'."


def test_random_validated():
    rng = random.Random(62)
    for _ in range(500):
        a = "".join(rng.choice("abc") for _ in range(rng.randint(0, 8)))
        b = "".join(rng.choice("abc") for _ in range(rng.randint(0, 8)))
        check(a, b, shortest_supersequence(a, b))


def test_large_input_in_time():
    rng = random.Random(6200)
    a = "".join(rng.choice("abcd") for _ in range(400))
    b = "".join(rng.choice("abcd") for _ in range(400))
    code = (
        "import sys\n"
        "from solution import shortest_supersequence\n"
        "a, b = sys.stdin.read().split()\n"
        "print(shortest_supersequence(a, b))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, input=a + " " + b, capture_output=True,
                           text=True, timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on two strings of 400 letters. A recursion on (i, j) without a memo is exponential: "
        "add a memo, or build the LCS table and walk back.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    check(a, b, r.stdout.strip())
