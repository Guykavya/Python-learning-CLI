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


EX = """addbook dune 1
addbook emma 2
borrow asha dune
borrow ravi dune
borrow asha dune
borrow asha emma
member asha
return ravi dune
return asha dune
borrow ravi dune
borrow asha zen
member kiran
close
"""


def test_example():
    assert run(EX) == [
        "dune: 1 copies available", "emma: 2 copies available", "asha borrowed dune",
        "dune is not available", "asha already has dune", "asha borrowed emma", "asha has: dune, emma",
        "ravi does not have dune", "asha returned dune", "ravi borrowed dune", "No such book zen",
        "kiran has nothing", "dune: 0/1", "emma: 1/2"]


def test_limit_of_three():
    cmds = "addbook a 1\naddbook b 1\naddbook c 1\naddbook d 1\nborrow m a\nborrow m b\nborrow m c\nborrow m d\nclose\n"
    out = run(cmds)
    assert out[7] == "m has reached the limit", "A member may hold at most 3 books."


def test_rule_order():
    cmds = "addbook a 1\naddbook b 1\naddbook c 1\naddbook d 0\nborrow m a\nborrow m b\nborrow m c\nborrow m a\nborrow m d\nclose\n"
    out = run(cmds)
    assert out[7] == "m already has a", "'already has' is checked before the limit."
    assert out[8] == "m has reached the limit", "The limit is checked before availability."


def test_addbook_twice():
    out = run("addbook x 1\naddbook x 2\nclose\n")
    assert out == ["x: 1 copies available", "x: 3 copies available", "x: 3/3"]


def test_nothing():
    assert run("close\n") == []
