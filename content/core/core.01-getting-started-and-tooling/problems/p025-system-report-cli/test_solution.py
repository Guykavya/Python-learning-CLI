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
import os
import platform
import re


def report(nickname, user, folder):
    b = "=" * 30
    return [b, f"System report for {nickname}", b, f"User: {user}",
            f"Python: {platform.python_version()} ({platform.python_implementation()})",
            f"OS: {platform.system()} {platform.release()}",
            f"Machine: {platform.machine()}",
            f"Folder: {folder}",
            f"In venv: {sys.prefix != sys.base_prefix}", b]


def env_user(value):
    env = {k: v for k, v in os.environ.items() if k != "USER"}
    if value is not None:
        env["USER"] = value
    return env


def test_full_report(tmp_path):
    out = run("kav\n", env=env_user("asha"), cwd=tmp_path)
    assert out == report("kav", "asha", os.path.realpath(tmp_path)), (
        "Compare line by line with problem.md:\n" + "\n".join(report("kav", "asha", os.path.realpath(tmp_path))))


def test_user_missing_is_unknown(tmp_path):
    out = run("kav\n", env=env_user(None), cwd=tmp_path)
    assert len(out) > 3 and out[3] == "User: unknown", (
        "When USER is not set, print 'unknown'. Use os.environ.get with a default.")


def test_python_line_format(tmp_path):
    out = run("x\n", env=env_user("a"), cwd=tmp_path)
    want = f"Python: {platform.python_version()} ({platform.python_implementation()})"
    assert len(out) > 4 and out[4] == want, (
        f"Expected {want!r}. print() with commas would add spaces inside the brackets; join with + instead.")


def test_nickname_with_spaces(tmp_path):
    out = run("Kavya B\n", env=env_user("a"), cwd=tmp_path)
    assert len(out) > 1 and out[1] == "System report for Kavya B", "Print the nickname exactly as typed."


def test_shebang_and_docstring():
    src = SOLUTION.read_text()
    assert src.splitlines()[0] == "#!/usr/bin/env python3", "The first line must be #!/usr/bin/env python3"
    assert ast.get_docstring(ast.parse(src)), (
        "Add a module docstring: a triple-quoted string as the first statement, saying what the script does.")


def test_style():
    src = SOLUTION.read_text()
    tree = ast.parse(src)
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
    bad = sorted(n for n in names if not re.match(r"^[a-z_][a-z0-9_]*$", n))
    assert not bad, f"Variable names must be snake_case: {bad}"
    long = [i for i, line in enumerate(src.splitlines(), 1) if len(line) > 79]
    assert not long, f"Lines longer than 79 characters: {long}"
