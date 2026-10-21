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

def test_example_stops_after_decline():
    assert run("1000\n+500\n-200\noops\n-2000\n+50\n") == [
        "#1 OK, balance 1500", "#2 OK, balance 1300", "Skipped: oops",
        "#3 declined: balance 1300, needed 2000", "Final balance: 1300"], (
        "After the decline, stop: the +50 line must not be processed.")


def test_decline_without_more_input():
    assert run("100\n-101\n") == ["#1 declined: balance 100, needed 101", "Final balance: 100"], (
        "After a decline, do not read another line (there is none, so reading would crash with EOFError).")


def test_exact_balance_allowed():
    assert run("300\n-300\nend\n") == ["#1 OK, balance 0", "Final balance: 0"], (
        "Withdrawing exactly the balance is allowed. Decline only when the amount is MORE than the balance.")


def test_end_immediately():
    assert run("42\nend\n") == ["Final balance: 42"], "No transactions: just the final balance."


def test_skipped_lines_not_counted():
    out = run("10\n+\n5\n+5x\n- 5\n\n+5\nend\n")
    assert out == ["Skipped: +", "Skipped: 5", "Skipped: +5x", "Skipped: - 5", "Skipped:",
                   "#1 OK, balance 15", "Final balance: 15"], (
        "A valid line is + or - followed only by digits. Invalid lines are skipped and not numbered. "
        "Check the length before looking at line[0].")


def test_zero_balance_start():
    assert run("0\n-1\n") == ["#1 declined: balance 0, needed 1", "Final balance: 0"], "Nothing to withdraw from."
