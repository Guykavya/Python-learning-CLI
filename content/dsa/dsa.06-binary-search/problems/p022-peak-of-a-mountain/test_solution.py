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



def play(n, p):
    def reply(i):
        assert 0 <= i < n, f"You asked about index {i}, but valid indices are 0 to {n - 1}."
        return i if i <= p else 2 * p - i

    final, queries = interact(f"{n}\n", reply, limit=2 * n.bit_length() + 4)
    assert final == str(p), (
        f"n = {n}, peak at {p}: you answered {final}. If a[mid] < a[mid + 1] the peak is right of mid (lo = mid + 1), else at mid or left (hi = mid).")


def test_all_small():
    for n in range(3, 12):
        for p in range(1, n - 1):
            play(n, p)


def test_huge():
    rng = random.Random(5)
    for n in (10**6, 10**9, 999999937):
        for p in (1, n - 2, n // 2, rng.randint(1, n - 2)):
            play(n, p)
