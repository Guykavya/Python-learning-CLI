import re
from pathlib import Path

_MIT = """MIT License

Copyright (c) <year> <your name>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

_PYPROJECT = """[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "0.1.0"
description = "Describe {name} in one sentence."
readme = "README.md"
requires-python = ">=3.11"
license = "MIT"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8", "mypy>=1.10", "ruff>=0.5"]

[tool.setuptools.package-data]
{name} = ["py.typed"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-ra -q"

[tool.ruff]
line-length = 88
src = ["src", "tests"]

[tool.mypy]
python_version = "3.11"
strict = true
files = ["src"]
"""

_INIT = '''"""{name}: describe the package here."""

__version__ = "0.1.0"

__all__ = ["__version__"]
'''

_TEST = """from {name} import __version__


def test_version_is_set():
    assert __version__ == "0.1.0"
"""

_README = """# {name}

Describe {name} in one sentence.

## Install

    python -m pip install .

Needs Python 3.11 or newer.

## Use

    >>> import {name}
    >>> {name}.__version__
    '0.1.0'

## Develop

    python -m venv .venv
    source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
    python -m pip install -e ".[dev]"
    python tasks.py check            # lint, types, tests
"""

_CHANGELOG = """# Changelog

All notable changes to this project are documented here.

## [Unreleased]

- Project created from the template.
"""

_GITIGNORE = """# Python
__pycache__/
*.py[cod]
*.egg-info/
build/
dist/

# Environments and secrets
.venv/
.env

# Tool caches
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Editors and OS
.vscode/
.idea/
.DS_Store
"""

# not filled with str.format: the runner has f-strings with braces
_TASKS = '''"""Project tasks.  Usage: python tasks.py <task>   (no argument lists them)."""

import subprocess
import sys

PY = [sys.executable, "-m"]

TASKS = {
    "test": ("run the tests", [[*PY, "pytest"]]),
    "lint": ("check style with ruff", [[*PY, "ruff", "check", "."], [*PY, "ruff", "format", "--check", "."]]),
    "types": ("check type hints with mypy", [[*PY, "mypy"]]),
}
TASKS["check"] = ("lint, types and tests", TASKS["lint"][1] + TASKS["types"][1] + TASKS["test"][1])


def main(argv):
    if len(argv) != 2 or argv[1] not in TASKS:
        print("usage: python tasks.py <task>")
        for name, (doc, _) in TASKS.items():
            print(f"  {name:6} {doc}")
        return 2
    for cmd in TASKS[argv[1]][1]:
        print("+", *cmd[1:], flush=True)
        code = subprocess.call(cmd)
        if code != 0:
            return code
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
'''


def make_project(root, name):
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
        raise ValueError(
            f"invalid project name {name!r}: use lowercase letters, digits and underscores, starting with a letter")
    project = Path(root) / name
    if project.exists():
        raise FileExistsError(str(project))
    files = {
        "pyproject.toml": _PYPROJECT.format(name=name),
        "README.md": _README.format(name=name),
        "CHANGELOG.md": _CHANGELOG,
        ".gitignore": _GITIGNORE,
        "LICENSE": _MIT,
        "tasks.py": _TASKS,
        f"src/{name}/__init__.py": _INIT.format(name=name),
        f"src/{name}/py.typed": "",
        f"tests/test_{name}.py": _TEST.format(name=name),
    }
    for rel, text in files.items():
        path = project / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    return project
