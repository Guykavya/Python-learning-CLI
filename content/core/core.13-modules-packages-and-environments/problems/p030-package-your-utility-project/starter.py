import json
import keyword
from pathlib import Path


def package_name(name):
    # TODO: "Word.Tools" -> "word_tools" (lowercase, runs of - _ . become one "_")
    return name


def make_project(root, name, *, package=None, version="0.1.0", description="Small text tools.",
                 dependencies=(), requires_python=">=3.10"):
    # TODO: check the arguments, then write pyproject.toml, README.md,
    # src/<package>/__init__.py, core.py, cli.py, __main__.py and tests/test_core.py
    # under Path(root) / name. Return that project folder.
    return Path(root) / name
