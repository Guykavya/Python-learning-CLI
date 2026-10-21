import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                       capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

from decimal import Decimal, ROUND_HALF_UP
import pytest

CENT = Decimal("0.01")


def expected(d, m, p):
    litres = Decimal(d) / Decimal(m)
    cost = litres * Decimal(p)
    return [f"Litres: {litres.quantize(CENT, rounding=ROUND_HALF_UP)}",
            f"Cost: {cost.quantize(CENT, rounding=ROUND_HALF_UP)}"]


def test_example():
    assert run("150\n12\n100\n") == ["Litres: 12.50", "Cost: 1250.00"], (
        "Litres is distance / mileage, not distance * mileage. Also check the space after 'Cost:' "
        "(sep='' removes it) and that litres show exactly 2 decimals.")


def test_decimal_distance():
    out = run("120.5\n10\n100\n")
    assert out == expected("120.5", "10", "100"), (
        "A distance like 120.5 must be accepted. int('120.5') raises ValueError; build a Decimal from the text.")


def test_half_cent_rounds_up():
    out = run("15\n10\n0.15\n")
    assert out[1] == "Cost: 0.23", (
        "Cost is exactly 0.225, which must round UP to 0.23. Two possible causes: price was built "
        "from a float (Decimal(float(...)) copies the binary error), or quantize() was called "
        "without rounding=ROUND_HALF_UP (the default is half-even).")


def test_litres_round_half_up():
    out = run("1.25\n10\n1\n")
    assert out[0] == "Litres: 0.13", (
        "0.125 litres must show as 0.13 (half up). round() uses half-even and gives 0.12. "
        "Use quantize(CENT, rounding=ROUND_HALF_UP).")


@pytest.mark.parametrize("d, m, p", [("100", "3", "102.86"), ("0", "15", "99.99"), ("987.6", "17.3", "104.21")])
def test_more(d, m, p):
    out = run(f"{d}\n{m}\n{p}\n")
    assert out == expected(d, m, p), (
        f"For {d} km at {m} km/l and Rs {p}, expected {expected(d, m, p)}, got {out}. "
        "Keep litres unrounded when computing the cost.")
