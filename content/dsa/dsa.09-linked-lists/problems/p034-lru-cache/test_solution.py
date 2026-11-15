import ast
import random
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

import pytest

from solution import LRUCache

HERE = Path(__file__).parent
SOLUTION = Path(__file__).with_name("solution.py")


def run_code(code, timeout, what):
    """Run code in a fresh Python process, so an endless loop fails cleanly instead of hanging."""
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what}: still running after {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


class Model:
    def __init__(self, capacity):
        self.capacity = capacity
        self.d = OrderedDict()

    def get(self, key):
        if key not in self.d:
            return -1
        self.d.move_to_end(key)
        return self.d[key]

    def put(self, key, value):
        if key in self.d:
            self.d.move_to_end(key)
        self.d[key] = value
        if len(self.d) > self.capacity:
            self.d.popitem(last=False)


def test_scripted_evictions():
    # Hand-traced (see problem.md): capacity 3.
    c = LRUCache(3)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    assert c.get("a") == 1, "a was put first and is still there."
    c.put("d", 4)
    assert c.get("b") == -1, (
        "put d on a full cache must evict the LEAST recently used key. get a had just used a, so b was the "
        "oldest: b must be gone. If a was evicted, get() does not move a key to the front.")
    c.put("c", 30)
    c.put("e", 5)
    assert c.get("a") == -1, (
        "put c 30 updated c (no eviction) and made c the most recent, so put e evicted a. "
        "If c was evicted instead, an update does not move the key to the front.")
    assert c.get("c") == 30, "c was updated to 30."
    assert c.get("d") == 4 and c.get("e") == 5, "d and e are in the cache."


def test_capacity_one():
    c = LRUCache(1)
    c.put(1, 1)
    c.put(2, 2)
    assert c.get(1) == -1 and c.get(2) == 2, "With capacity 1 every new key evicts the previous one."
    c.put(2, 20)
    assert c.get(2) == 20, "Updating the only key must not evict it."


def test_update_does_not_grow():
    c = LRUCache(2)
    c.put(1, 1)
    c.put(1, 2)
    c.put(2, 2)
    assert c.get(1) == 2 and c.get(2) == 2, (
        "Putting key 1 twice must update it, not store a second node; after put 2 both keys fit in capacity 2.")


def test_random_against_ordereddict():
    rng = random.Random(34)
    for capacity in (1, 2, 3, 5, 8):
        c, m = LRUCache(capacity), Model(capacity)
        for step in range(1000):
            key = rng.randint(0, 10)
            if rng.random() < 0.5:
                assert c.get(key) == m.get(key), (
                    f"capacity {capacity}, step {step}: get({key}) should be {m.get(key)}. "
                    f"The keys from least to most recent should be {list(m.d)}.")
            else:
                v = rng.randint(0, 99)
                c.put(key, v)
                m.put(key, v)


def test_no_ordereddict():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    imports = {a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) for a in n.names}
    assert "OrderedDict" not in names | attrs | imports and "move_to_end" not in attrs, (
        "Build the LRU order yourself with a doubly linked list; OrderedDict is the model the tests use.")


def test_operations_are_constant_time():
    code = (
        "from solution import LRUCache\n"
        "c = LRUCache(10000)\n"
        "total = 0\n"
        "for i in range(100000):\n"
        "    c.put(i, i)\n"
        "    total += c.get(i - 5000)\n"
        "print(total)\n"
    )
    out = run_code(code, 20, "100,000 puts and 100,000 gets on a cache of capacity 10,000 (a list scan per "
                             "operation is O(capacity); use a dict plus a doubly linked list)")
    m = Model(10000)
    want = 0
    for i in range(100000):
        m.put(i, i)
        want += m.get(i - 5000)
    assert out == str(want), f"Expected the total {want} (computed with the OrderedDict model), got {out!r}."
