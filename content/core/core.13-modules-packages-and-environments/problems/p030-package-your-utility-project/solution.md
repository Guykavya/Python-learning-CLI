## Approach

A generator is three steps:

1. **Validate everything up front.** Name rules, import-name rules, version format, and "the target
   folder is new or empty". Nothing is written until all checks pass, so a bad call leaves no half-made
   project behind.
2. **Templates for the files.** The package files are fixed text with a few holes. Placeholders such
   as `__PKG__` filled with `str.replace` keep the generated code readable (no doubled braces).
   `pyproject.toml` is built line by line, and every value goes through `json.dumps`, so quotes and
   backslashes are escaped correctly.
3. **Write the tree** with `Path.mkdir(parents=True, exist_ok=True)` and `write_text(encoding="utf-8")`.

The generated package follows the rules of the module:

- **src layout**: only an installed (or explicitly added) package can be imported, never the project
  folder by accident;
- **`__init__.py` is the public API**: it re-exports from `core.py` and lists `__all__`;
- **`core.py` has no I/O**, so it is easy to test and reuse; **`cli.py`** is the thin layer that
  parses arguments, prints and returns an exit code;
- **`__main__.py`** makes `python -m word_tools` work, and **`[project.scripts]`** makes pip create a
  `word-tools` command. Both end up calling the same `main`.

## Code

See `reference.py` for the full file. The core of `make_project`:

```python
def make_project(root, name, *, package=None, version="0.1.0", description="Small text tools.",
                 dependencies=(), requires_python=">=3.10"):
    if not valid_project_name(name):
        raise ValueError(f"invalid project name: {name!r}")
    if package is None:
        package = package_name(name)
    if not package.isidentifier() or keyword.iskeyword(package):
        raise ValueError(f"invalid package name: {package!r}")
    if not valid_version(version):
        raise ValueError(f"invalid version: {version!r}")

    project = Path(root) / name
    if project.exists() and (not project.is_dir() or any(project.iterdir())):
        raise FileExistsError(f"{project} exists and is not empty")

    pkg_dir = Path("src") / package
    files = {
        Path("pyproject.toml"): pyproject_text(name, package, version, description,
                                               list(dependencies), requires_python),
        Path("README.md"): README_MD,
        pkg_dir / "__init__.py": INIT_PY,
        pkg_dir / "core.py": CORE_PY,
        pkg_dir / "cli.py": CLI_PY,
        pkg_dir / "__main__.py": MAIN_PY,
        Path("tests") / "test_core.py": TEST_PY,
    }
    for rel, template in files.items():
        path = project / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        text = template if rel.name == "pyproject.toml" else fill(template, name, package, version, description)
        path.write_text(text, encoding="utf-8")
    return project
```

The generated `cli.py`:

```python
import argparse
import sys

from . import __version__
from .core import slugify, word_count


def build_parser():
    parser = argparse.ArgumentParser(prog="word-tools", description="Small text tools.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    slug = sub.add_parser("slug", help="turn text into a URL slug")
    slug.add_argument("text", nargs="+", help="the words to turn into a slug")
    count = sub.add_parser("count", help="count the words in a file")
    count.add_argument("file", nargs="?", default="-", help="a text file, or - for stdin")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "slug":
        print(slugify(" ".join(args.text)))
        return 0
    if args.file == "-":
        text = sys.stdin.read()
    else:
        try:
            with open(args.file, encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print(f"error: cannot read {args.file}: {e.strerror}", file=sys.stderr)
            return 1
    print(word_count(text))
    return 0
```

## Complexity

Linear in the size of the generated text: seven small files.

## Another way

- **One source for the version.** Instead of writing the version into `__init__.py`, the package can
  ask the installed metadata: `from importlib.metadata import version; __version__ = version("word-tools")`.
  That only works once the package is installed, which is why this project writes it in both places
  from one argument.
- **Other build back-ends.** `hatchling`, `flit_core` or `uv_build` work the same way: only the
  `[build-system]` table changes. `uv init --package word-tools` generates a project like yours.
- **Templates from files.** Big generators (cookiecutter, copier) keep the templates as real files in
  a folder and copy them, which is easier to edit than strings in Python code.
