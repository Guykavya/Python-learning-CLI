import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from solution import make_project

EXPECTED = ["pyproject.toml", "README.md", "CHANGELOG.md", ".gitignore", "LICENSE", "tasks.py",
            "src/{n}/__init__.py", "src/{n}/py.typed", "tests/test_{n}.py"]


def test_files_exist(tmp_path):
    p = make_project(tmp_path, "pricekit")
    assert p == tmp_path / "pricekit", "Return the path of the new project folder, root / name."
    for rel in EXPECTED:
        assert (p / rel.format(n="pricekit")).is_file(), f"Missing file: {rel.format(n='pricekit')}"
    assert (p / "src/pricekit/py.typed").read_bytes() == b"", "py.typed is an empty marker file."


def test_pyproject_is_valid_and_complete(tmp_path):
    p = make_project(tmp_path, "tinytool")
    data = tomllib.loads((p / "pyproject.toml").read_text(encoding="utf-8"))
    proj = data["project"]
    assert proj["name"] == "tinytool" and proj["version"] == "0.1.0" and proj["requires-python"] == ">=3.11"
    assert data["tool"]["pytest"]["ini_options"]["pythonpath"] == ["src"]
    assert data["tool"]["pytest"]["ini_options"]["testpaths"] == ["tests"]
    assert data["tool"]["setuptools"]["package-data"] == {"tinytool": ["py.typed"]}, "package-data must name the package."
    deps = list(proj.get("dependencies", [])) + [d for g in proj["optional-dependencies"].values() for d in g]
    assert deps, "The dev extras must list pytest, mypy and ruff."
    for d in deps:
        assert re.search(r"(>=|==|~=)\s*\d", d), f"Dependency {d!r} has no lower bound."


def test_readme_changelog_gitignore_license(tmp_path):
    p = make_project(tmp_path, "my_tool")
    readme = (p / "README.md").read_text(encoding="utf-8")
    assert readme.startswith("# my_tool\n"), "The README starts with the project name as a title."
    for section in ("## Install", "## Use", "## Develop"):
        assert section in readme.splitlines(), f"README is missing the section {section!r}."
    assert "## [Unreleased]" in (p / "CHANGELOG.md").read_text(encoding="utf-8").splitlines()
    ignore = (p / ".gitignore").read_text(encoding="utf-8").splitlines()
    for line in ("__pycache__/", ".venv/", ".env", ".pytest_cache/"):
        assert line in ignore, f".gitignore must contain {line!r}."
    assert (p / "LICENSE").read_text(encoding="utf-8").startswith("MIT License")


def test_no_placeholder_is_left_and_name_is_used(tmp_path):
    p = make_project(tmp_path, "pricekit")
    for f in p.rglob("*"):
        if f.is_file():
            text = f.read_bytes().decode("utf-8")
            assert "{name}" not in text and "{n}" not in text, f"A placeholder is left in {f.name}."
            assert "\r" not in text, f"{f.name} must use \\n line endings."
    assert "from pricekit import" in (p / "tests/test_pricekit.py").read_text(encoding="utf-8")
    assert "__version__" in (p / "src/pricekit/__init__.py").read_text(encoding="utf-8")


@pytest.mark.parametrize("bad", ["my-proj", "1abc", "Abc", "", "a b", "a.b", "-x"])
def test_invalid_names(tmp_path, bad):
    with pytest.raises(ValueError):
        make_project(tmp_path, bad)
    assert list(tmp_path.iterdir()) == [], "Nothing may be created for an invalid name."


def test_existing_folder_is_not_overwritten(tmp_path):
    (tmp_path / "pricekit").mkdir()
    (tmp_path / "pricekit" / "keep.txt").write_text("mine", encoding="utf-8")
    with pytest.raises(FileExistsError):
        make_project(tmp_path, "pricekit")
    assert (tmp_path / "pricekit" / "keep.txt").read_text(encoding="utf-8") == "mine", "Do not touch an existing folder."
    assert [f.name for f in (tmp_path / "pricekit").iterdir()] == ["keep.txt"]


def test_the_fresh_clone_test_runs_the_projects_own_tests(tmp_path):
    p = make_project(tmp_path, "pricekit")
    env = {**os.environ, "PYTHONPATH": str(p / "src")}
    env.pop("PYTEST_CURRENT_TEST", None)
    r = subprocess.run([sys.executable, "-m", "pytest", "-o", "addopts=", "-p", "no:cacheprovider"], cwd=p, env=env,
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, f"The new project's own tests must pass. Output:\n{r.stdout[-800:]}{r.stderr[-400:]}"
    assert "1 passed" in r.stdout, "The template ships exactly one passing test."


def test_task_runner_prints_usage_and_exits_2(tmp_path):
    p = make_project(tmp_path, "pricekit")
    r = subprocess.run([sys.executable, "tasks.py"], cwd=p, capture_output=True, text=True, timeout=30)
    assert r.returncode == 2, "tasks.py without an argument must exit with code 2."
    lines = r.stdout.splitlines()
    assert lines[0] == "usage: python tasks.py <task>"
    for name in ("test", "lint", "types", "check"):
        assert any(line.strip().startswith(name) for line in lines[1:]), f"tasks.py must list the task {name}."
    r = subprocess.run([sys.executable, "-m", "py_compile", "tasks.py"], cwd=p, capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, "tasks.py must be valid Python."
