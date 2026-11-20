import pathlib
import random
import subprocess
import sys

from solution import IterSeg

HERE = pathlib.Path(__file__).parent


def add(x, y):
    return x + y


def matmul(x, y):
    """2x2 integer matrices as tuples (a, b, c, d): not commutative."""
    a, b, c, d = x
    e, f, g, h = y
    return (a * e + b * g, a * f + b * h, c * e + d * g, c * f + d * h)


I2 = (1, 0, 0, 1)


def test_chapter_example():
    it = IterSeg([5, 3, 8, 6, 2, 7, 4, 1], add, 0)
    assert it.t[1:] == [36, 22, 14, 8, 14, 9, 5, 5, 3, 8, 6, 2, 7, 4, 1], f"t[1:] got {it.t[1:]}."
    assert len(it.t) == 16, "The iterative tree has exactly 2n entries."
    assert (it.query(2, 7), it.query(0, 8), it.query(3, 4), it.query(6, 6)) == (27, 36, 6, 0)


def test_order_with_strings():
    words = IterSeg(list("segmenttree"), add, "")
    got = words.query(2, 7)
    assert got == "gment", (
        f"Concatenation of a[2:7] should be 'gment', got {got!r}. Keep two accumulators: resl = f(resl, t[l]) "
        "and resr = f(t[r], resr); return f(resl, resr).")
    assert words.query(0, 11) == "segmenttree" and words.query(4, 4) == ""


def test_random_strings_and_matrices():
    rng = random.Random(1606)
    for _ in range(60):
        n = rng.randint(1, 50)
        s = [rng.choice("abcd") for _ in range(n)]
        m = [(rng.randint(-2, 2), rng.randint(-2, 2), rng.randint(-2, 2), rng.randint(-2, 2)) for _ in range(n)]
        ts, tm = IterSeg(s, add, ""), IterSeg(m, matmul, I2)
        assert len(ts.t) == 2 * n, "Size exactly 2n."
        for step in range(35):
            if rng.random() < 0.4:
                i = rng.randrange(n)
                s[i] = rng.choice("abcd")
                m[i] = (rng.randint(-2, 2), rng.randint(-2, 2), rng.randint(-2, 2), rng.randint(-2, 2))
                ts.update(i, s[i])
                tm.update(i, m[i])
            else:
                l = rng.randint(0, n)
                r = rng.randint(l, n)
                assert ts.query(l, r) == "".join(s[l:r]), f"n={n}: order broken on [{l},{r}) of {''.join(s)}."
                want = I2
                for x in m[l:r]:
                    want = matmul(want, x)
                assert tm.query(l, r) == want, f"n={n}: matrix product on [{l},{r}) is wrong (left/right order)."


BIG_CODE = (
    "import random\n"
    "from solution import IterSeg\n"
    "rng = random.Random(166)\n"
    "n = 2 * 10**5\n"
    "it = IterSeg([rng.randint(-10**6, 10**6) for _ in range(n)], min, float('inf'))\n"
    "x = 0\n"
    "for _ in range(10**5):\n"
    "    if rng.random() < 0.5:\n"
    "        it.update(rng.randrange(n), rng.randint(-10**6, 10**6))\n"
    "    else:\n"
    "        x ^= it.query(rng.randint(0, n // 10), rng.randint(9 * n // 10, n))\n"
    "print(x)\n"
)
BIG_WANT = ['-999999']


def test_large_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, "too slow: each query must be O(log n). Climb from both ends; do not scan the range."
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
