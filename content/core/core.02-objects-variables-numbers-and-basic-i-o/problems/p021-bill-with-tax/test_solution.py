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


def expected(price, qty, rate):
    sub = (Decimal(price) * qty).quantize(CENT, rounding=ROUND_HALF_UP)
    tax = (sub * Decimal(rate) / 100).quantize(CENT, rounding=ROUND_HALF_UP)
    return [f"Subtotal: {sub}", f"Tax: {tax}", f"Total: {sub + tax}"]


def test_example():
    assert run("19.99\n2\n18\n") == ["Subtotal: 39.98", "Tax: 7.20", "Total: 47.18"]


def test_half_cent_rounds_up():
    out = run("1.15\n1\n50\n")
    assert out[1] == "Tax: 0.58", (
        "The tax is exactly 0.575, which must round UP to 0.58. A float stores 0.575 as "
        "0.57499999..., so float formatting gives 0.57. Use Decimal and ROUND_HALF_UP.")


def test_half_up_not_half_even():
    out = run("0.25\n1\n10\n")
    assert out[1] == "Tax: 0.03", (
        "0.025 must become 0.03. The default Decimal rounding (ROUND_HALF_EVEN) gives 0.02. "
        "Pass rounding=ROUND_HALF_UP to quantize().")


@pytest.mark.parametrize("price, qty, rate", [("5", 2, "0"), ("0.10", 3, "12.5"), ("999.99", 7, "28"), ("0.01", 1, "5")])
def test_more(price, qty, rate):
    out = run(f"{price}\n{qty}\n{rate}\n")
    assert out == expected(price, qty, rate), (
        f"For {price} x {qty} at {rate}% expected {expected(price, qty, rate)}, got {out}. "
        "Every amount needs exactly 2 decimals: quantize(Decimal('0.01')).")
