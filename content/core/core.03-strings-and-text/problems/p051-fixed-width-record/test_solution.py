import os
import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines.

    Spaces at the end of each line are ignored, and so are blank lines at the very end.
    """
    r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin, capture_output=True,
                       text=True, encoding="utf-8", timeout=10,
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    lines = [line.rstrip() for line in r.stdout.split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return lines


def record(acc, name, city, paise):
    return f"{acc:06}{name:<20}{city:<10}{paise:010}"


def test_example():
    assert run("000042Asha Kumar          Pune      0000123456\n") == [
        "ID: 42", "Name: Asha Kumar", "City: Pune", "Amount: Rs 1,234.56"]


def test_full_width_name():
    rec = record(7, "Venkataraman Krishna", "Chennai", 99)
    assert run(rec + "\n") == ["ID: 7", "Name: Venkataraman Krishna", "City: Chennai", "Amount: Rs 0.99"], (
        "A name can use all 20 columns. The name slice is record[6:26].")


def test_small_paise_two_digits():
    assert run(record(1, "Ravi", "Delhi", 1005) + "\n")[3] == "Amount: Rs 10.05", "Paise must always have two digits: :02."


def test_large_amount():
    assert run(record(999999, "Big Corp", "Mumbai", 9876543210) + "\n") == [
        "ID: 999999", "Name: Big Corp", "City: Mumbai", "Amount: Rs 98,765,432.10"], (
        "Use // 100 and % 100 on the integer, with , for thousands separators.")


def test_unicode_name():
    assert run(record(12, "Zoë Ångström", "Malmö", 50000) + "\n") == [
        "ID: 12", "Name: Zoë Ångström", "City: Malmö", "Amount: Rs 500.00"]


def test_zero_amount():
    assert run(record(5, "X", "Y", 0) + "\n")[3] == "Amount: Rs 0.00"
