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
            f"Your program did not finish within {timeout} seconds. Look for an infinite loop, "
            "an input() that waits for more lines than the test gives, or a slow step such as "
            "`in` on a long list inside a loop (use a set or dict instead).") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]


def test_example():
    data = "5\nasha ravi\nasha meena\nravi john\nmeena john\nravi kiran\n2\nasha\nkiran\n"
    assert run(data) == ["asha: john (2), kiran (1)", "kiran: asha (1), john (1)"]


def test_unknown_person():
    assert run("1\na b\n1\nzed\n") == ["zed: no suggestions"], "Use friends.get(name, set()) for unknown names."


def test_no_self_no_existing():
    out = run("3\na b\nb c\na c\n1\na\n")
    assert out == ["a: no suggestions"], (
        "a's friends are b and c, who are friends with each other. Do not suggest a to itself, "
        "and do not suggest existing friends.")


def test_both_directions():
    out = run("2\nx y\nz y\n1\nx\n")
    assert out == ["x: z (1)"], "Friendship goes both ways: store y -> x and y -> z as well."


def test_top_three_only():
    lines = ["6", "p hub", "hub a", "hub b", "hub c", "hub d", "p hub", "1", "p"]
    out = run("\n".join(lines) + "\n")
    assert out == ["p: a (1), b (1), c (1)"], "Show at most three, ties by name. Repeated lines change nothing."
