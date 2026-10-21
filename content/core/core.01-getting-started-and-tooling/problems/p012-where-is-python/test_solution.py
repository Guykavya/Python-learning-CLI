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

import os
import platform


def expected(cwd):
    return [
        f"Executable: {sys.executable}",
        f"Version: {platform.python_version()}",
        f"Implementation: {platform.python_implementation()}",
        f"System: {platform.system()}",
        f"Folder: {cwd}",
    ]


def test_report(tmp_path):
    assert run(cwd=tmp_path) == expected(os.path.realpath(tmp_path)), (
        "Print the five lines in order: Executable, Version, Implementation, System, Folder.")


def test_folder_is_current_directory(tmp_path):
    sub = tmp_path / "another folder"
    sub.mkdir()
    out = run(cwd=sub)
    assert out and out[-1] == f"Folder: {os.path.realpath(sub)}", (
        "Folder must be os.getcwd(), the folder the script is run FROM, not where the file is.")


def test_executable_line_first(tmp_path):
    out = run(cwd=tmp_path)
    assert out and out[0] == f"Executable: {sys.executable}", (
        "Use sys.executable, the full path of the interpreter running your script.")
