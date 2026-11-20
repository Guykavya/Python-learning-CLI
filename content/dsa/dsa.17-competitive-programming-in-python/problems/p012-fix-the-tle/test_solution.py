import re
import subprocess
import sys
import time
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")

RUNNER = r"""
import builtins, runpy, sys
calls = {"input": 0, "write": 0}
_input = builtins.input
def counted_input(*a):
    calls["input"] += 1
    return _input(*a)
builtins.input = counted_input
class W:
    def __init__(self, real):
        self.real = real
    def write(self, x):
        calls["write"] += 1
        return self.real.write(x)
    def __getattr__(self, name):
        return getattr(self.real, name)
sys.stdout = W(sys.stdout)
try:
    runpy.run_path(sys.argv[1], run_name="__main__")
finally:
    sys.stdout.real.flush()
    sys.stderr.write("\nCALLS %d %d\n" % (calls["input"], calls["write"]))
"""


def run_counted(stdin, timeout=20):
    """Run solution.py; return (stdout, stderr, input_calls, write_calls, seconds)."""
    t0 = time.perf_counter()
    try:
        r = subprocess.run([sys.executable, "-c", RUNNER, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"Your program did not finish in {timeout} seconds. It is far too slow for this input.")
    sec = time.perf_counter() - t0
    m = re.search(r"CALLS (\d+) (\d+)", r.stderr)
    ins, wr = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr[-800:]}"
    return r.stdout, r.stderr, ins, wr, sec


def run(stdin, timeout=20):
    """Plain run: return the printed lines (right-stripped)."""
    out = run_counted(stdin, timeout)[0]
    return [line.rstrip() for line in out.strip().splitlines()]



import random


def model(ops):
    from collections import deque
    d = deque()
    res = []
    for op in ops:
        if op[0] == "push":
            d.append(op[1])
        elif op[0] == "pop":
            res.append(str(d.popleft()) if d else "empty")
        else:
            res.append(str(len(d)))
    return res


def to_text(ops):
    return f"{len(ops)}\n" + "".join(("push %d\n" % o[1]) if o[0] == "push" else o[0] + "\n" for o in ops)


def test_example():
    assert run("6\npush 5\npush 7\npop\nsize\npop\npop\n") == ["5", "1", "7", "empty"]


def test_correct_on_random_small_input():
    rng = random.Random(12)
    ops = []
    for _ in range(300):
        k = rng.choice(["push", "push", "pop", "size"])
        ops.append(("push", rng.randint(-100, 100)) if k == "push" else (k,))
    assert run(to_text(ops)) == model(ops), "The fast version must compute exactly the same answers as the slow one."


def test_big_queue_is_fast():
    n = 200000
    ops = [("push", i) for i in range(n)] + [("pop",)] * n + [("size",)]
    stdin = to_text(ops)
    out, err, ins, wr, sec = run_counted(stdin, timeout=60)
    want = model(ops)
    assert out.split() == want, "Wrong output on the big input."
    assert ins <= 1000, f"input() was called {ins} times: read everything with sys.stdin.read().split()."
    assert wr <= 1000, f"{wr} writes to standard output: collect the lines in a list and print once."
    assert sec <= 3.0, (
        f"{sec:.1f} s. list.pop(0) moves every remaining element, so 200000 pops cost about n*n/2 moves. "
        "Use collections.deque and popleft().")
