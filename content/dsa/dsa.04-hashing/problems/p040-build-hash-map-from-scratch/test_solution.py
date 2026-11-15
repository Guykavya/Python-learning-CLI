import subprocess
import sys
from pathlib import Path

import pytest

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or a loop that does far more work than needed.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import random
import re


def ask(cmds, timeout=10):
    return run(f"{len(cmds)}\n" + "\n".join(cmds) + "\n", timeout=timeout)


def test_no_builtin_containers():
    text = SOLUTION.read_text()
    text = "\n".join(line.split("#")[0] for line in text.splitlines())
    bad = re.findall(r"\bdict\b|\bset\b|\bCounter\b|\bdefaultdict\b|\bOrderedDict\b|[{}]", text)
    assert not bad, (
        f"This problem is about BUILDING the table: found {sorted(set(bad))} in your code. "
        "Use a list of buckets and lists inside them (no braces, dict or set; f-strings use braces too, so print with commas).")


def test_example():
    cmds = ["put 0 1", "put 8 2", "put 16 3", "maxchain", "get 8", "get 9", "del 8", "del 8", "size", "buckets"]
    assert ask(cmds) == ["3", "2", "none", "ok", "missing", "2", "8"], (
        "Expected 3 2 none ok missing 2 8. Keys 0, 8, 16 share bucket 0 (key % 8), so maxchain is 3.")


def test_update_and_delete():
    cmds = ["put 5 10", "put 5 20", "size", "get 5", "del 5", "get 5", "size", "maxchain"]
    assert ask(cmds) == ["1", "20", "ok", "none", "0", "0"], (
        "Putting an existing key replaces its value and does not change the size; deleting removes it; an empty table has maxchain 0.")


def test_resize_happens_on_seventh_new_key():
    keys = [0, 8, 16, 24, 32, 40]
    cmds = [f"put {k} 1" for k in keys] + ["buckets", "maxchain", "put 48 1", "buckets", "maxchain"]
    assert ask(cmds) == ["8", "6", "16", "4"], (
        "6 keys in 8 buckets: 6*4 = 24 is not above 8*3 = 24, so no resize and all 6 share bucket 0 (maxchain 6). "
        "The 7th key: 28 > 24, so m becomes 16 and the keys split: bucket 0 holds 0, 16, 32, 48 (4) and bucket 8 holds 8, 24, 40.")


def test_updates_never_resize():
    cmds = [f"put {k} 1" for k in range(6)] + [f"put 3 {v}" for v in range(50)] + ["buckets", "size"]
    assert ask(cmds) == ["8", "6"], "Only inserting a NEW key can trigger a resize; updating key 3 again and again must not."


def test_deleting_does_not_shrink():
    cmds = [f"put {k} 1" for k in range(7)] + ["buckets"] + [f"del {k}" for k in range(7)] + ["buckets", "size"]
    assert ask(cmds) == ["16"] + ["ok"] * 7 + ["16", "0"], "7 keys cause one resize to 16; deletions leave m at 16."


class Model:
    def __init__(self):
        self.m = 8
        self.t = [[] for _ in range(8)]
        self.n = 0

    def find(self, k):
        for p in self.t[k % self.m]:
            if p[0] == k:
                return p
        return None

    def run(self, cmd):
        p = cmd.split()
        if p[0] == "put":
            k, v = int(p[1]), int(p[2])
            e = self.find(k)
            if e:
                e[1] = v
                return None
            self.t[k % self.m].append([k, v])
            self.n += 1
            if self.n * 4 > self.m * 3:
                pairs = [x for ch in self.t for x in ch]
                self.m *= 2
                self.t = [[] for _ in range(self.m)]
                for x in pairs:
                    self.t[x[0] % self.m].append(x)
            return None
        if p[0] == "get":
            e = self.find(int(p[1]))
            return str(e[1]) if e else "none"
        if p[0] == "del":
            k = int(p[1])
            e = self.find(k)
            if e:
                self.t[k % self.m].remove(e)
                self.n -= 1
                return "ok"
            return "missing"
        if p[0] == "size":
            return str(self.n)
        if p[0] == "buckets":
            return str(self.m)
        return str(max(len(c) for c in self.t))


def expected_for(cmds):
    mo = Model()
    out = []
    for c in cmds:
        r = mo.run(c)
        if r is not None:
            out.append(r)
    return out


def random_cmds(rng, count, key_range):
    cmds = []
    for _ in range(count):
        r = rng.random()
        k = rng.randint(0, key_range)
        if r < 0.45:
            cmds.append(f"put {k} {rng.randint(0, 10**9)}")
        elif r < 0.7:
            cmds.append(f"get {k}")
        elif r < 0.85:
            cmds.append(f"del {k}")
        elif r < 0.92:
            cmds.append("size")
        elif r < 0.99:
            cmds.append("buckets")
        else:
            cmds.append("maxchain")
    return cmds


def test_random_small():
    rng = random.Random(44)
    for _ in range(30):
        cmds = random_cmds(rng, rng.randint(5, 60), 40)
        assert ask(cmds) == expected_for(cmds), (
            f"Commands {cmds}: expected {expected_for(cmds)}. Check the resize rule (new key, size*4 > m*3, rehash from bucket 0) and delete.")


def test_large():
    rng = random.Random(45)
    cmds = random_cmds(rng, 60000, 10**6)
    assert ask(cmds) == expected_for(cmds), (
        "60000 commands. Resize by doubling and rehashing so chains stay short; a table that never grows has chains of length n / 8.")
