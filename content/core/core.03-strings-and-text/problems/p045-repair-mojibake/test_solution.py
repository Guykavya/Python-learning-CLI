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


def garble(text):
    return text.encode("utf-8").decode("latin-1")


def test_example():
    assert run("naÃ¯ve rÃ©sumÃ©\n") == ["Fixed: naïve résumé", "Shorter by: 3"], (
        "Reverse the damage: .encode('latin-1') to get the bytes back, then .decode('utf-8').")


def test_ascii_unchanged():
    assert run("plain text\n") == ["Fixed: plain text", "Shorter by: 0"], "ASCII has no mojibake and must come back unchanged."


def test_many_scripts():
    original = "Zoë, Ångström, Straße"
    assert run(garble(original) + "\n") == [f"Fixed: {original}", "Shorter by: 4"]


def test_rupee_three_bytes():
    assert run(garble("₹500") + "\n") == ["Fixed: ₹500", "Shorter by: 2"], "₹ is three UTF-8 bytes, so it shrinks by 2."


def test_hindi():
    original = "नमस्ते"
    assert run(garble(original) + "\n") == [f"Fixed: {original}", f"Shorter by: {2 * len(original)}"]


def test_empty():
    assert run("\n") == ["Fixed:", "Shorter by: 0"]
