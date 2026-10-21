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
    cmds = "stock pen 10 5\nstock ink 4 30\nstock pad 20 5\nsell pen 3\nsell ink 5\nsell glue 1\nstock pen 2 6\nlow 10\nreport\nend\n"
    assert run(cmds) == [
        "Stocked pen: 10", "Stocked ink: 4", "Stocked pad: 20", "Sold 3 pen for 15",
        "Not enough ink (have 4)", "Unknown item glue", "Stocked pen: 9", "ink 4", "pen 9",
        "ink 4 x 30 = 120", "pad 20 x 5 = 100", "pen 9 x 6 = 54", "Total value: 274", "Revenue: 15"]


def test_nothing():
    assert run("end\n") == ["Revenue: 0"]


def test_empty_report_and_low():
    assert run("report\nlow 5\nend\n") == ["Total value: 0", "No low stock", "Revenue: 0"]


def test_zero_quantity_items_stay():
    out = run("stock a 2 10\nsell a 2\nlow 1\nreport\nend\n")
    assert out == ["Stocked a: 2", "Sold 2 a for 20", "a 0", "a 0 x 10 = 0", "Total value: 0", "Revenue: 20"], (
        "An item with quantity 0 stays in the inventory and is low stock.")


def test_low_is_strictly_below():
    out = run("stock a 5 1\nstock b 4 1\nlow 5\nend\n")
    assert out[2:] == ["b 4", "Revenue: 0"], "low N lists quantities BELOW N, so 5 is not low."


def test_report_ties_by_name():
    out = run("stock b 2 5\nstock a 1 10\nstock c 10 2\nreport\nend\n")
    assert out[3:6] == ["c 10 x 2 = 20", "a 1 x 10 = 10", "b 2 x 5 = 10"], (
        "Highest value first; equal values in name order. Sort (-value, name) tuples.")


def test_new_price_used_for_sales():
    out = run("stock x 5 10\nstock x 0 20\nsell x 1\nend\n")
    assert out[2] == "Sold 1 x for 20", "stock sets the new price, which later sales use."
