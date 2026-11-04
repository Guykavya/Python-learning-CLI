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



INF = 2147483647


def play(n, t):
    def reply(i):
        assert i >= 0, "Indices start at 0; you asked for a negative index."
        return 2 * i - 1000 if i < n else INF

    final, queries = interact(f"{t}\n", reply, limit=2 * n.bit_length() + 6)
    want = (t + 1000) // 2 if (t + 1000) % 2 == 0 and 0 <= (t + 1000) // 2 < n else -1
    assert final == str(want), (
        f"n = {n}, target {t}: expected {want}, you answered {final}. Double hi until a[hi] >= t (INF counts as too large), then search [hi // 2, hi].")


def test_tiny_arrays():
    for n in range(1, 8):
        for t in range(-1002, 2 * n - 995):
            play(n, t)


def test_medium():
    rng = random.Random(7)
    for n in (100, 1000, 12345):
        for _ in range(8):
            i = rng.randrange(n)
            play(n, 2 * i - 1000)
            play(n, 2 * i - 999)
        play(n, 2 * n - 1000)
        play(n, 2 * (n - 1) - 1000)


def test_huge_hidden_length():
    rng = random.Random(8)
    for n in (10**6, 10**9):
        for i in (0, 1, n - 1, rng.randrange(n)):
            play(n, 2 * i - 1000)
        play(n, 2 * n - 1000 - 1)
        play(n, 5)
