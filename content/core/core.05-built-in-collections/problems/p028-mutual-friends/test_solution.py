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
    assert run("asha: ravi meena kiran\nravi: asha kiran john\n") == [
        "Mutual: kiran", "Suggest to asha: john", "Suggest to ravi: meena", "Network size: 5"], (
        "Do not suggest a person to themselves: subtract {name} as well.")


def test_empty_lists():
    assert run("a:\nb:\n") == ["Mutual: none", "Suggest to a: none", "Suggest to b: none", "Network size: 2"]


def test_repeats():
    out = run("x: y y z\nw: z z\n")
    assert out == ["Mutual: z", "Suggest to x: none", "Suggest to w: y", "Network size: 4"], (
        "Repeated names count once; sets do this for you.")


def test_sorted_output():
    out = run("p: d c b a\nq: h g f e\n")
    assert out[1] == "Suggest to p: e f g h" and out[2] == "Suggest to q: a b c d", (
        "Sort names before printing; sets have no order.")
