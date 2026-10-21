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


def block(f):
    return [f"Name: {f.__name__}", f"Type: {type(f).__name__}",
            f"Module: {f.__module__}", f"Doc: {f.__doc__}"]


def test_output():
    assert run() == block(abs) + block(len), "Print Name, Type, Module and Doc for abs, then for len."


def test_type_line():
    out = run()
    assert len(out) > 1 and out[1] == "Type: builtin_function_or_method", (
        "Use type(abs).__name__. Printing type(abs) itself shows <class '...'>.")


def test_reads_attributes():
    tree = ast.parse(SOLUTION.read_text())
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert {"__name__", "__module__", "__doc__"} <= attrs, (
        "Read the attributes __name__, __module__ and __doc__ from the objects.")
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Name) and n.func.id == "type"]
    assert calls, "Get the type with type(...)."


def test_doc_not_pasted():
    tree = ast.parse(SOLUTION.read_text())
    texts = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    assert not any("absolute value" in t or "number of items" in t for t in texts), (
        "Do not paste the documentation text. Read it from abs.__doc__ and len.__doc__.")
