# Project: package one of your utilities

Until now your code lived in single files that you ran with `python file.py`. A real tool is a
**package** that anyone can install with pip, import from any folder, and run as a command. In this
project you write a *project generator*: one call creates a complete, installable, tested
src-layout project for a small text utility. Then (optionally) you install it for real in a fresh
virtual environment.

## The utility

The package offers two functions and a command line with two sub-commands:

- `slugify(text)`: lowercase; keep letters and digits; every run of other characters becomes **one**
  `-`; no `-` at the start or the end. `"Hello, World!"` -> `"hello-world"`,
  `"Python 3.13 is out"` -> `"python-3-13-is-out"`, `"!!!"` -> `""`.
- `word_count(text)`: `len(text.split())`.
- `<name> slug WORDS...` prints the slug of the words joined with spaces.
- `<name> count [FILE]` prints the number of words in `FILE`; with no file or `-`, it reads stdin.

## What to write

In `solution.py`, write:

### `package_name(name)`

The import name for a project name: lowercase, and every run of `-`, `_` and `.` becomes **one**
`_`. `"word-tools"` -> `"word_tools"`, `"Word.Tools_2"` -> `"word_tools_2"`.

### `make_project(root, name, *, package=None, version="0.1.0", description="Small text tools.", dependencies=(), requires_python=">=3.10")`

Create the folder `Path(root) / name` and return it. `name` is the **project name** (what you
`pip install`, and also the command name). `package` is the **import name**; if it is `None`, use
`package_name(name)`.

**Check first, write after.** Raise before you create anything:

- `ValueError` if `name` is empty, has a character other than ASCII letters, digits, `-`, `_` and
  `.`, or does not start and end with a letter or digit;
- `ValueError` if the package name is not a valid identifier or is a keyword (`str.isidentifier()`,
  `keyword.iskeyword()`), for example `"1st_tool"` or `"class"`;
- `ValueError` if `version` is not one or more groups of digits joined by dots (`"1.2.0"`, `"2.5"`);
- `FileExistsError` if `root / name` exists and is not an empty folder. Never overwrite anything.

**The files** (for `make_project(root, "word-tools")`):

```text
word-tools/
├── pyproject.toml
├── README.md
├── src/
│   └── word_tools/
│       ├── __init__.py     re-exports slugify and word_count, __all__, __version__
│       ├── core.py         slugify and word_count (no printing)
│       ├── cli.py          build_parser() and main(argv=None) -> int, with argparse
│       └── __main__.py     so that `python -m word_tools ...` works
└── tests/
    └── test_core.py        real pytest tests for the package
```

**`pyproject.toml`** must contain:

```toml
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "word-tools"
version = "0.1.0"
description = "Small text tools."
readme = "README.md"
requires-python = ">=3.10"
dependencies = []

[project.scripts]
"word-tools" = "word_tools.cli:main"

[tool.setuptools.packages.find]
where = ["src"]
```

Strings in TOML are in double quotes, and a `"` or `\` inside them must be escaped. A dependency
like `tomli>=2; python_version < "3.11"` contains quotes. Tip: `json.dumps(text)` produces a string
that is also a valid TOML basic string.

**`src/<package>/__init__.py`**: imports `slugify` and `word_count` from `.core`, sets
`__all__ = ["slugify", "word_count"]` and `__version__` to the version (the same value as in
`pyproject.toml`). It prints nothing.

**`src/<package>/cli.py`**: `main(argv=None)` parses `argv` (or `sys.argv[1:]` when it is `None`)
with `argparse`:

- `prog` is the project name, so the help starts with `usage: word-tools`;
- `--version` prints `word-tools 0.1.0` and exits 0 (`action="version"`);
- sub-commands `slug` (one or more words) and `count` (an optional file, default `-`), with
  `add_subparsers(dest="command", required=True)`, so no sub-command is a usage error (exit 2);
- `main` **returns** 0 on success. If the file cannot be read, it prints `error: ...` to stderr and
  returns 1 (no traceback).

**`src/<package>/__main__.py`**: calls `sys.exit(main())`, guarded by
`if __name__ == "__main__":`, so that importing it runs nothing.

**`tests/test_core.py`**: at least one real test that passes when you run `python -m pytest` in the
project with the package importable.

**`README.md`**: starts with `# <name>`, says how to install (`pip install ...`) and shows how to use
the command (`<name> slug ...`).

## How the tests check your project (no installing!)

The tests never run pip. They:

1. read `pyproject.toml` with `tomllib` and check every field;
2. put `<project>/src` on `sys.path` and import the package;
3. run `python -m word_tools --help`, `--version`, `slug ...` and `count ...` in a subprocess with
   `PYTHONPATH=src`, and check the output and exit codes;
4. take the entry point string `"word_tools.cli:main"`, import the module, get `main`, and call it
   (that is all a console script does);
5. run the project's own tests with `python -m pytest tests`.

## Example

```python
>>> from solution import make_project
>>> make_project("out", "word-tools")
PosixPath('out/word-tools')
```

```bash
$ cd out/word-tools
$ PYTHONPATH=src python -m word_tools slug "Packaging is FUN!"
packaging-is-fun
$ echo "one two three" | PYTHONPATH=src python -m word_tools count
3
$ PYTHONPATH=src python -m word_tools --version
word-tools 0.1.0
$ PYTHONPATH=src python -m word_tools count nope.txt; echo "exit $?"
error: cannot read nope.txt: No such file or directory
exit 1
```

(On Windows PowerShell, set the variable with `$env:PYTHONPATH = "src"` first.)

## Optional final step: install it for real in a fresh environment

This is the project of the module: your utility, installed like any package from PyPI. Do it by hand,
outside the tests. It needs the internet once, because pip downloads `setuptools` to build the package.

```bash
# 1. generate the project into a folder outside this course, for example ~/projects
#    (run this in the folder that holds your solution.py for this problem)
mkdir -p ~/projects
python -c "from solution import make_project; print(make_project('$HOME/projects', 'word-tools'))"
cd ~/projects

# 2. a fresh, empty virtual environment
python -m venv fresh-env
source fresh-env/bin/activate            # Windows: fresh-env\Scripts\activate
pip list                                  # only pip: nothing else is installed

# 3. install your project into it (a normal install builds a wheel and copies it)
pip install ./word-tools
pip show word-tools                       # name, version, location in site-packages

# 4. use it from ANY folder: the command was created from [project.scripts]
cd /tmp
word-tools slug "It works, Kavya!"
python -c "import word_tools; print(word_tools.__version__, word_tools.__file__)"

# 5. for development: an editable install points site-packages back at src/
cd ~/projects/word-tools
pip install -e . pytest
python -m pytest

# 6. clean up
deactivate
rm -rf ~/projects/fresh-env
```

With uv the same steps are `uv venv fresh-env`, `uv pip install ./word-tools`. To build a wheel file you
could share, run `pip install build` and then `python -m build` inside the project: it writes
`dist/word_tools-0.1.0-py3-none-any.whl` and a `.tar.gz`.

Look at `word_tools.__file__` in step 4: it is inside `fresh-env/.../site-packages`, not your project
folder. That is the src layout doing its job (see p027).
