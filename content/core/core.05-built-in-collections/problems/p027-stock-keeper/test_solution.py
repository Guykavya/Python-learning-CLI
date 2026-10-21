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
    cmds = "add pen 10\nadd ink 3\nsell pen 4\nsell ink 5\ncheck ink\ncheck glue\nsell ink 3\nadd pad 2\nend\n"
    assert run(cmds) == ["Cannot sell 5 ink: only 3 left", "ink: 3", "glue: 0", "Stock:", "pad 2", "pen 6"], (
        "A failed sale changes nothing. Sold-out items are left out of the report.")


def test_nothing():
    assert run("end\n") == ["Stock:", "(nothing in stock)"]


def test_sell_unknown_item():
    assert run("sell cake 1\nend\n") == ["Cannot sell 1 cake: only 0 left", "Stock:", "(nothing in stock)"], (
        "An item never added has 0. Use get(item, 0) to avoid KeyError.")


def test_add_twice_adds_up():
    assert run("add a 2\nadd a 3\ncheck a\nend\n") == ["a: 5", "Stock:", "a 5"], (
        "Quantities must be numbers. '2' + '3' as text would give '23'.")


def test_exact_sale():
    assert run("add x 4\nsell x 4\nend\n") == ["Stock:", "(nothing in stock)"], (
        "Selling exactly what is there is allowed and leaves 0.")
