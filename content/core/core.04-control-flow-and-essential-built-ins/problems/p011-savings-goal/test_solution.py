import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or an input() call waiting for a line that never comes.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import pytest


def expected(goal, deposit, rate):
    balance, months = 0.0, 0
    while balance < goal:
        balance += balance * rate / 100
        balance += deposit
        months += 1
    return [f"Months: {months}", f"Balance: {balance:.2f}"]


def test_example():
    assert run("1000\n300\n0\n") == ["Months: 4", "Balance: 1200.00"], (
        "300 a month with no interest: 300, 600, 900, 1200. Stop at the first balance >= goal.")


def test_exactly_reaching_goal():
    assert run("900\n300\n0\n") == ["Months: 3", "Balance: 900.00"], (
        "A balance exactly equal to the goal has reached it. Use < in the loop condition, not <=.")


@pytest.mark.parametrize("goal, deposit, rate", [(10000, 1000, 1.5), (5000, 250, 0.5), (100000, 2000, 2), (1, 1, 50)])
def test_with_interest(goal, deposit, rate):
    got = run(f"{goal}\n{deposit}\n{rate}\n")
    assert got == expected(goal, deposit, rate), (
        f"goal={goal}, deposit={deposit}, rate={rate}: expected {expected(goal, deposit, rate)}, got {got}. "
        "Each month: interest on the current balance first, then the deposit.")


@pytest.mark.parametrize("goal", ["0", "-50"])
def test_goal_already_reached(goal):
    assert run(f"{goal}\n100\n1\n") == ["Months: 0", "Balance: 0.00"], (
        "A goal of 0 or less is reached before any month passes.")


def test_zero_goal_with_zero_deposit():
    assert run("0\n0\n5\n") == ["Months: 0", "Balance: 0.00"], (
        "A goal of 0 is already reached, even with no deposit.")


def test_unreachable():
    assert run("500\n0\n10\n", timeout=5) == ["Goal not reachable"], (
        "With 0 deposit the balance stays 0 for ever. Detect this before the loop instead of looping for ever.")
