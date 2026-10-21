import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str = "", env=None, exe=None, cwd=None) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    r = subprocess.run([exe or sys.executable, str(SOLUTION)], input=stdin,
                       capture_output=True, text=True, timeout=10, env=env, cwd=cwd)
    assert r.returncode == 0, f"Your program crashed. Read the traceback:\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import ast


def _prints():
    tree = ast.parse(SOLUTION.read_text())
    return [n for n in ast.walk(tree) if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name) and n.func.id == "print"]


def test_output():
    assert run() == ["18/10/2026", "Loading...done"], (
        "Expected '18/10/2026' then 'Loading...done'. If you see '18 10 2026', you forgot sep.")


def test_date_print_uses_sep_and_variables():
    ok = False
    for call in _prints():
        kw = {k.arg for k in call.keywords}
        names = {a.id for a in call.args if isinstance(a, ast.Name)}
        if "sep" in kw and {"day", "month", "year"} <= names:
            ok = True
    assert ok, "Use one call like print(day, month, year, sep=...). Do not type 18/10/2026 as text."


def test_loading_uses_end():
    assert any("end" in {k.arg for k in c.keywords} for c in _prints()), (
        "The first of the two calls on line 2 needs end=... so the next print continues on the same line.")
