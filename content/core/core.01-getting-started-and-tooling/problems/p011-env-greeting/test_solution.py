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


def env_with(**values):
    env = {k: v for k, v in os.environ.items() if k not in ("LEARNER_NAME", "LEARNER_LEVEL")}
    env.update(values)
    return env


def test_both_set():
    assert run(env=env_with(LEARNER_NAME="Asha", LEARNER_LEVEL="expert")) == ["Hello, Asha!", "Level: expert"], (
        "Read LEARNER_NAME and LEARNER_LEVEL with os.environ.get.")


def test_neither_set_uses_defaults():
    assert run(env=env_with()) == ["Hello, stranger!", "Level: beginner"], (
        "When a variable is missing, use the default. os.environ[...] crashes with KeyError; "
        "os.environ.get(name, default) does not.")


def test_only_name_set():
    assert run(env=env_with(LEARNER_NAME="Ravi")) == ["Hello, Ravi!", "Level: beginner"], (
        "Each variable has its own default.")


def test_name_with_space():
    assert run(env=env_with(LEARNER_NAME="Asha Rao"))[0] == "Hello, Asha Rao!", (
        "Use the value exactly as given. There is no space before the '!'.")
