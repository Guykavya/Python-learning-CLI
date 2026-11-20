import pathlib
import random
import subprocess
import sys

from solution import DSU

HERE = pathlib.Path(__file__).parent


class Model:
    """Groups as a list of labels; union relabels a whole group (slow but obviously right)."""

    def __init__(self, n):
        self.label = list(range(n))

    def union(self, x, y):
        a, b = self.label[x], self.label[y]
        if a == b:
            return False
        self.label = [a if c == b else c for c in self.label]
        return True

    def connected(self, x, y):
        return self.label[x] == self.label[y]

    def count(self):
        return len(set(self.label))

    def size(self, x):
        return self.label.count(self.label[x])


def test_example():
    d = DSU(5)
    assert (d.union(0, 1), d.union(2, 3), d.union(1, 3)) == (True, True, True), "Three unions of different groups each return True."
    assert d.union(0, 2) is False, "0 and 2 are already together after the three unions: union returns False."
    assert d.connected(3, 0) is True and d.connected(4, 0) is False, "3 is with 0; 4 is alone."
    assert d.count() == 2, "Groups {0,1,2,3} and {4}: count() is 2. Lower the counter only when union really merges."
    assert d.size(2) == 4, "size(2) is 4. Keep sizes on the ROOTS and read size of find(x)."
    assert d.size(4) == 1, "4 is alone: size 1."


def test_find_returns_a_common_root():
    d = DSU(6)
    d.union(0, 1)
    d.union(2, 3)
    d.union(4, 5)
    d.union(1, 3)
    roots = {d.find(x) for x in range(4)}
    assert len(roots) == 1, f"0, 1, 2, 3 are one group, but find gave different roots {roots}. union must link the ROOTS."
    assert d.find(4) == d.find(5) != d.find(0), "{4, 5} is a separate group with its own root."
    assert d.find(d.find(2)) == d.find(2), "The root is its own root."


def test_union_links_roots_not_elements():
    d = DSU(4)
    d.union(0, 1)
    d.union(2, 1)
    d.union(3, 0)
    assert all(d.connected(0, x) for x in range(4)), (
        "After union(0,1), union(2,1), union(3,0) all four are together. If 0 lost its group, union set parent[x] = y "
        "on the element instead of on its root.")
    assert d.size(1) == 4 and d.count() == 1, "One group of 4."


def test_random_against_model():
    rng = random.Random(43)
    for t in range(60):
        n = rng.randint(1, 15)
        d, m = DSU(n), Model(n)
        for step in range(60):
            x, y = rng.randrange(n), rng.randrange(n)
            op = rng.choice(["union", "union", "connected", "size", "count", "find"])
            if op == "union":
                assert d.union(x, y) == m.union(x, y), f"test {t} step {step}: union({x}, {y}) returned the wrong bool."
            elif op == "connected":
                assert d.connected(x, y) == m.connected(x, y), f"test {t} step {step}: connected({x}, {y}) is wrong."
            elif op == "size":
                assert d.size(x) == m.size(x), f"test {t} step {step}: size({x}) should be {m.size(x)}, got {d.size(x)}."
            elif op == "count":
                assert d.count() == m.count(), f"test {t} step {step}: count() should be {m.count()}, got {d.count()}."
            else:
                r = d.find(x)
                assert 0 <= r < n and m.connected(r, x), f"test {t} step {step}: find({x}) = {r} is not in {x}'s group."


def test_many_operations_time_limit():
    code = (
        "from solution import DSU\n"
        "n = 100000\n"
        "d = DSU(n)\n"
        "for i in range(n - 1):\n"
        "    d.union(i, i + 1)\n"
        "ok = all(d.connected(0, n - 1) for _ in range(n))\n"
        "print(ok, d.count(), d.size(12345))\n"
        "e = DSU(n)\n"
        "for i in range(n - 1, 0, -1):\n"
        "    e.union(i, i - 1)\n"
        "print(all(e.connected(n - 1, i % n) for i in range(0, n, 3)), e.count())\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=15, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (15 s) on 100,000 unions along a line followed by 100,000 queries. Without union by size AND "
        "without path compression every find walks a chain of 100,000 elements. Use both tricks.")
    assert "RecursionError" not in r.stderr, (
        "RecursionError: a recursive find on a long chain passes the recursion limit. Write find with loops.")
    assert r.returncode == 0, "Your DSU crashed on the big test:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["True", "1", "100000", "True", "1"], (
        f"Big test: expected one group of 100,000; got {r.stdout.split()}.")
