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
    cmds = "join asha\njoin ravi\njoin asha\nshow\nserve\nleave meena\njoin meena\nleave ravi\nshow\nserve\nserve\nend\n"
    assert run(cmds) == [
        "asha is already in the queue", "Queue: asha ravi", "Serving asha",
        "meena is not in the queue", "Queue: meena", "Serving meena", "Nobody to serve"]


def test_front_is_served_first():
    assert run("join a\njoin b\njoin c\nserve\nshow\nend\n") == ["Serving a", "Queue: b c"], (
        "The front is index 0. pop() with no index takes the back; use pop(0).")


def test_empty_show():
    assert run("show\nend\n") == ["Queue: (empty)"]


def test_leave_middle():
    assert run("join a\njoin b\njoin c\nleave b\nshow\nend\n") == ["Queue: a c"], (
        "leave removes the person from the middle with remove().")


def test_rejoin_after_serve():
    assert run("join a\nserve\njoin a\nshow\nend\n") == ["Serving a", "Queue: a"], (
        "Once served, a person is no longer in the queue and may join again.")
