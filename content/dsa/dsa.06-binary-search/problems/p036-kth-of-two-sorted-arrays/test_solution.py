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
from bisect import bisect_left, bisect_right


import threading


def interact(header, reply, limit, timeout=10):
    """Start your program, send `header`, answer each line '? i' with reply(i),
    stop at the line '! answer'. Returns (answer_text, number_of_queries)."""
    p = subprocess.Popen([sys.executable, str(SOLUTION)], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    timer = threading.Timer(timeout, p.kill)
    timer.start()
    queries, final = 0, None
    try:
        try:
            p.stdin.write(header)
            p.stdin.flush()
            while True:
                line = p.stdout.readline()
                if not line:
                    break
                line = line.strip()
                if line.startswith("?"):
                    queries += 1
                    assert queries <= limit, (
                        f"Your program asked more than {limit} questions. A binary search needs only about "
                        "log2(n) of them. Are you stepping one by one instead of halving?")
                    args = [int(t) if t.lstrip("-").isdigit() else t for t in line[1:].split()]
                    p.stdin.write(str(reply(*args)) + "\n")
                    p.stdin.flush()
                elif line.startswith("!"):
                    final = line[1:].strip()
                    break
                else:
                    raise AssertionError(
                        f"Unexpected output line {line!r}. Print only '? i' (with flush=True) or '! answer'.")
        except (BrokenPipeError, OSError):
            pass
    finally:
        timer.cancel()
        p.kill()
        err = p.stderr.read()
        p.wait()
    assert final is not None, (
        "Your program ended, crashed or timed out before printing '! answer'. "
        "Did you forget flush=True on every print? A never-ending loop also lands here.\n" + err[-500:])
    return final, queries



class Seq:
    def __init__(self, n, f):
        self.n, self.f = n, f

    def __len__(self):
        return self.n

    def __getitem__(self, i):
        if not 0 <= i < self.n:
            raise IndexError(i)
        return self.f(i)


def kth(A, B, k):
    lo, hi = min(A[0], B[0]), max(A[len(A) - 1], B[len(B) - 1])
    while lo < hi:
        mid = (lo + hi) // 2
        if bisect_right(A, mid) + bisect_right(B, mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo


def play(n, m, k, a0, b0):
    A = Seq(n, lambda i: i * i // 3 + a0)
    B = Seq(m, lambda j: 5 * j + b0)

    def reply(which, i):
        seq = {"A": A, "B": B}.get(which)
        assert seq is not None, f"The line must look like '? A i' or '? B j', not '? {which} {i}'."
        assert 0 <= i < len(seq), f"You asked for {which}[{i}], but {which} has indices 0 to {len(seq) - 1}."
        return seq[i]

    final, queries = interact(f"{n} {m} {k}\n", reply, limit=4 * max(n, m).bit_length() + 8)
    want = kth(A, B, k)
    assert final == str(want), (
        f"n = {n}, m = {m}, k = {k}: expected {want}, you answered {final}. "
        "Binary search i = how many of the k smallest come from A; i is too small when A[i] < B[k - i - 1]; the answer is max(A[i - 1], B[k - i - 1]).")


def test_all_small():
    for n in range(1, 5):
        for m in range(1, 5):
            for a0, b0 in ((1, 2), (3, 1), (7, 7)):
                for k in range(1, n + m + 1):
                    play(n, m, k, a0, b0)


def test_medium():
    rng = random.Random(9)
    for _ in range(25):
        n, m = rng.randint(1, 3000), rng.randint(1, 3000)
        play(n, m, rng.randint(1, n + m), rng.randint(1, 100), rng.randint(1, 100))


def test_huge():
    rng = random.Random(10)
    for n, m in ((10**9, 10**9), (1, 10**9), (10**9, 1), (123456789, 987654321)):
        for k in (1, n + m, (n + m) // 2, rng.randint(1, n + m)):
            play(n, m, k, 4, 9)
