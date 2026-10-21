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
import shutil


def test_first_line_is_shebang():
    first = SOLUTION.read_text().splitlines()[0] if SOLUTION.read_text() else ""
    assert first == "#!/usr/bin/env python3", (
        f"The very first line must be exactly #!/usr/bin/env python3 . Yours is: {first!r}")


def test_output_with_python():
    assert run() == ["Running as: __main__", "Script file: solution.py"], (
        "Print __name__ and os.path.basename(__file__) with the labels from problem.md.")


def test_runs_directly(tmp_path):
    target = tmp_path / "solution.py"
    shutil.copy(SOLUTION, target)
    os.chmod(target, 0o755)
    env = dict(os.environ, PATH=os.path.dirname(sys.executable) + os.pathsep + os.environ.get("PATH", ""))
    r = subprocess.run(["./solution.py"], cwd=tmp_path, capture_output=True, text=True, timeout=10, env=env)
    assert r.returncode == 0, f"Running ./solution.py failed. Check the shebang line.\n{r.stderr}"
    assert r.stdout.split()[-1:] == ["solution.py"], "Running directly should still print the file name."


def test_uses_dunder_names():
    src = SOLUTION.read_text()
    assert "__name__" in src and "__file__" in src, (
        "Use the special names __name__ and __file__ rather than typing the values.")
