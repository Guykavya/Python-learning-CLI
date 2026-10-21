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


def test_example():
    assert run("202\n") == ["bin: 11001010", "oct: 312", "hex: ca", "prefixed: 0b11001010 0o312 0xca",
                            "byte: 11001010", "grouped: 1100_1010"]


def test_zero():
    assert run("0\n") == ["bin: 0", "oct: 0", "hex: 0", "prefixed: 0b0 0o0 0x0", "byte: 00000000", "grouped: 0"], (
        "Zero is 0 in every base. 08b pads it to eight zeros.")


def test_small_is_padded():
    assert run("5\n")[4] == "byte: 00000101", "Use 08b to pad with zeros, not spaces."


def test_large_not_cut():
    out = run("1000000\n")
    assert out[4] == "byte: 11110100001001000000", "Width is a minimum; long numbers are shown in full."
    assert out[5] == "grouped: 1111_0100_0010_0100_0000"
    assert out[2] == "hex: f4240"
