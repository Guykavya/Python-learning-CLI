import math
import pathlib
import random
import subprocess
import sys

from solution import FenwickTree, SegmentTree, SparseTable

HERE = pathlib.Path(__file__).parent


def harness(name, make, ask, answer, update=None, apply=None, n_range=(1, 40), trials=40, steps=60, seed=1630,
            value=lambda rng: rng.randint(-30, 30), allow_empty=True):
    """Run random operations on a structure and on a plain list; stop at the first difference."""
    rng = random.Random(seed)
    for trial in range(trials):
        n = rng.randint(*n_range)
        a = [value(rng) for _ in range(n)]
        s = make(list(a))
        for step in range(steps):
            if update is not None and rng.random() < 0.4:
                i, v = rng.randrange(n), value(rng)
                update(s, i, v)
                apply(a, i, v)
            else:
                l = rng.randint(0, n - (0 if allow_empty else 1))
                r = rng.randint(l if allow_empty else l + 1, n)
                got, want = ask(s, l, r), answer(a[l:r])
                assert got == want, f"{name}: trial {trial} step {step}, [{l}, {r}) of {a}: expected {want!r}, got {got!r}."


def setv(a, i, v):
    a[i] = v


def addv(a, i, v):
    a[i] += v


def test_examples():
    fw = FenwickTree([5, 3, 8, 6, 2, 7, 4, 1])
    assert fw.range_sum(2, 7) == 27 and FenwickTree(4).prefix(4) == 0
    st = SegmentTree(list("segment"), lambda x, y: x + y, "")
    st.update(0, "S")
    assert st.query(0, 4) == "Segm"
    assert SparseTable([5, 3, 8, 6, 2, 7, 4, 1], min).query(1, 7) == 2


def test_fenwick_sum():
    harness("FenwickTree(list)", FenwickTree, lambda s, l, r: s.range_sum(l, r), sum,
            update=lambda s, i, v: s.add(i, v), apply=addv)


def test_fenwick_from_size():
    def make(a):
        fw = FenwickTree(len(a))
        for i, x in enumerate(a):
            fw.add(i, x)
        return fw
    harness("FenwickTree(n) + adds", make, lambda s, l, r: s.range_sum(l, r), sum,
            update=lambda s, i, v: s.add(i, v), apply=addv, seed=16301)


def test_fenwick_build_equals_adds():
    rng = random.Random(16302)
    for _ in range(30):
        a = [rng.randint(-9, 9) for _ in range(rng.randint(1, 40))]
        slow = FenwickTree(len(a))
        for i, x in enumerate(a):
            slow.add(i, x)
        built = FenwickTree(a)
        assert [built.prefix(r) for r in range(len(a) + 1)] == [slow.prefix(r) for r in range(len(a) + 1)], (
            "FenwickTree(list) must give the same prefix sums as n calls to add.")


def test_segment_tree_operations():
    ops = [("sum", lambda x, y: x + y, 0, sum),
           ("min", min, math.inf, lambda xs: min(xs, default=math.inf)),
           ("gcd", math.gcd, 0, lambda xs: math.gcd(*xs) if xs else 0)]
    for name, f, e, brute in ops:
        harness(f"SegmentTree({name})", lambda a, f=f, e=e: SegmentTree(a, f, e), lambda s, l, r: s.query(l, r),
                brute, update=lambda s, i, v: s.update(i, v), apply=setv, seed=hash(name) % 1000,
                value=lambda rng: rng.randint(0, 30))


def test_segment_tree_keeps_order():
    harness("SegmentTree(concat)", lambda a: SegmentTree(a, lambda x, y: x + y, ""), lambda s, l, r: s.query(l, r),
            lambda xs: "".join(xs), update=lambda s, i, v: s.update(i, v), apply=setv, seed=16303,
            value=lambda rng: rng.choice("abcd"))


def test_sparse_table():
    for name, f, brute in [("min", min, min), ("max", max, max), ("gcd", math.gcd, lambda xs: math.gcd(*xs))]:
        harness(f"SparseTable({name})", lambda a, f=f: SparseTable(a, f), lambda s, l, r: s.query(l, r), brute,
                seed=16304, value=lambda rng: rng.randint(1, 60), allow_empty=False)


BIG_CODE = (
    "import random\n"
    "from solution import FenwickTree, SegmentTree, SparseTable\n"
    "rng = random.Random(1630)\n"
    "n = 2 * 10**5\n"
    "a = [rng.randint(-10**9, 10**9) for _ in range(n)]\n"
    "fw, st, sp = FenwickTree(a), SegmentTree(a, min, float('inf')), SparseTable(a, max)\n"
    "x = 0\n"
    "for _ in range(10**5):\n"
    "    l, r = rng.randint(0, n // 10), rng.randint(9 * n // 10, n)\n"
    "    if rng.random() < 0.5:\n"
    "        i, v = rng.randrange(n), rng.randint(-10**9, 10**9)\n"
    "        fw.add(i, v)\n"
    "        st.update(i, v)\n"
    "    else:\n"
    "        x ^= fw.range_sum(l, r) ^ st.query(l, r) ^ sp.query(l, r)\n"
    "print(x)\n"
)
BIG_WANT = ['-264457702852']


def test_large_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG_CODE], cwd=HERE, capture_output=True, text=True,
                           timeout=60, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, "too slow: each query must be O(log n) (O(1) for the sparse table)."
    assert r.returncode == 0, "Your library crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == BIG_WANT, f"Large input: expected {BIG_WANT}, got {r.stdout.split()}."
