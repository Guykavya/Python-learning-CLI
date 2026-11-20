# The professional project template

Chapter section 17 builds the project `pricekit` by hand, step by step. Automate it: write

```python
make_project(root, name)
```

that creates the folder `root/name` with the template and returns its `Path`:

```text
name/
  pyproject.toml          # build system, [project] name/version/requires-python, dev extras, pytest/ruff/mypy settings
  README.md               # "# name", then the sections "## Install", "## Use", "## Develop"
  CHANGELOG.md            # contains a "## [Unreleased]" section
  .gitignore              # at least __pycache__/, .venv/, .env, .pytest_cache/
  LICENSE                 # MIT text
  tasks.py                # a pure-Python task runner (test, lint, types, check)
  src/name/__init__.py    # defines __version__ = "0.1.0"
  src/name/py.typed       # empty
  tests/test_name.py      # one passing test that imports the package
```

Requirements:

- `name` must match `[a-z][a-z0-9_]*` (a valid, lowercase package name): otherwise raise `ValueError` (for example `"my-proj"`, `"1abc"`, `"Abc"`, `""`).
- If the folder `root/name` already exists, raise `FileExistsError` and change nothing.
- The `name` appears everywhere it belongs: in the pyproject `name`, in `package-data`, in the README title, in the folder `src/name`, in the test's import. No `{name}` placeholder may be left in any file.
- `pyproject.toml` must be valid TOML, `requires-python` is `">=3.11"`, `pythonpath = ["src"]` and `testpaths = ["tests"]` are set, and every dependency (also in `dev`) has a lower bound (it must pass your `check_pyproject` of the earlier problem).
- Files are written as UTF-8 bytes with `\n` line endings.
- **The fresh-clone test:** the tests run `python -m pytest` inside the new project (with `PYTHONPATH=src`) in a subprocess; it must exit with code 0. `python tasks.py` without an argument must print the usage line `usage: python tasks.py <task>` and exit with code 2.

## Example

```python
from pathlib import Path
p = make_project(Path("/tmp/work"), "pricekit")
print(p)        # /tmp/work/pricekit
```
