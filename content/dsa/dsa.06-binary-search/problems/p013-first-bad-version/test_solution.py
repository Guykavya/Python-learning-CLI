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



def play(n, b):
    final, queries = interact(f"{n}\n", lambda v: 1 if v >= b else 0, limit=n.bit_length() + 1)
    assert final == str(b), f"n = {n}, first bad version {b}: you answered {final}. Is the answer the first True (hi = mid) and not mid + 1?"
    return queries


def test_tiny():
    for n in range(1, 9):
        for b in range(1, n + 1):
            play(n, b)


def test_ends():
    for n in (10, 1000, 10**9):
        play(n, 1)
        play(n, n)
        play(n, n - 1)


def test_huge_n():
    rng = random.Random(3)
    for _ in range(20):
        n = rng.randint(10**17, 10**18)
        play(n, rng.randint(1, n))
