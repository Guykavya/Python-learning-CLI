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
    assert run("  Asha.Kumar@Example.COM\n") == ["User: Asha.Kumar", "Domain: example.com", "Masked: A***@example.com"], (
        "Strip the line, cut at '@' with partition, and lowercase only the domain.")


def test_single_letter_user():
    assert run("x@y.in\n") == ["User: x", "Domain: y.in", "Masked: x***@y.in"]


def test_plus_address():
    assert run("ravi+news@Mail.Example.org\n") == ["User: ravi+news", "Domain: mail.example.org", "Masked: r***@mail.example.org"]


def test_user_case_kept():
    assert run("BigBoss@X.COM\n")[0] == "User: BigBoss", "Keep the user part exactly as typed. Only the domain is lowercased."


def test_unicode_user():
    assert run("élodie@exemple.fr\n")[2] == "Masked: é***@exemple.fr"
