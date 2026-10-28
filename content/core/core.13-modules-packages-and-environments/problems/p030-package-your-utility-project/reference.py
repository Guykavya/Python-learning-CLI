"""Generate an installable src-layout project for a small text utility."""
import json
import keyword
from pathlib import Path

INIT_PY = '''"""__NAME__: small text tools."""
from .core import slugify, word_count

__all__ = ["slugify", "word_count"]
__version__ = "__VERSION__"
'''

CORE_PY = '''"""The utility functions. No printing, no input: easy to test and to reuse."""


def slugify(text):
    """'Hello, World!' -> 'hello-world'"""
    out = []
    for ch in text.lower():
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != "-":
            out.append("-")
    return "".join(out).strip("-")


def word_count(text):
    return len(text.split())
'''

CLI_PY = '''"""Command line interface for __NAME__."""
import argparse
import sys

from . import __version__
from .core import slugify, word_count


def build_parser():
    parser = argparse.ArgumentParser(prog="__NAME__", description="Small text tools.")
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
'''

MAIN_PY = '''import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
'''

TEST_PY = '''from __PKG__ import slugify, word_count
from __PKG__.cli import main


def test_slugify():
    assert slugify("Hello, World!") == "hello-world"


def test_word_count():
    assert word_count("one two  three\\n") == 3


def test_cli_slug(capsys):
    assert main(["slug", "Hi", "there"]) == 0
    assert capsys.readouterr().out == "hi-there\\n"
'''

README_MD = '''# __NAME__

__DESCRIPTION__

## Install

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install .                    # or: pip install -e . while you work on it
```

## Use

```bash
__NAME__ slug "Hello, World!"     # hello-world
__NAME__ count notes.txt          # number of words
python -m __PKG__ --version
```

## Develop

```bash
pip install -e . pytest
python -m pytest
```
'''


def toml_string(value):
    """A TOML basic string. JSON string escapes are valid TOML escapes."""
    return json.dumps(value)


def toml_list(values):
    return "[" + ", ".join(toml_string(v) for v in values) + "]"


def package_name(name):
    """PEP 503 style: lowercase, runs of - _ . become one underscore."""
    out = []
    for ch in name.lower():
        if ch in "-_.":
            if not out or out[-1] != "_":
                out.append("_")
        else:
            out.append(ch)
    return "".join(out)


def valid_project_name(name):
    allowed = all(ch.isascii() and (ch.isalnum() or ch in "-_.") for ch in name)
    return bool(name) and allowed and name[0].isalnum() and name[-1].isalnum()


def valid_version(version):
    return bool(version) and all(part.isdigit() for part in version.split("."))


def pyproject_text(name, package, version, description, dependencies, requires_python):
    return "\n".join([
        "[build-system]",
        'requires = ["setuptools>=61"]',
        'build-backend = "setuptools.build_meta"',
        "",
        "[project]",
        f"name = {toml_string(name)}",
        f"version = {toml_string(version)}",
        f"description = {toml_string(description)}",
        'readme = "README.md"',
        f"requires-python = {toml_string(requires_python)}",
        f"dependencies = {toml_list(dependencies)}",
        "",
        "[project.scripts]",
        f"{toml_string(name)} = {toml_string(package + '.cli:main')}",
        "",
        "[tool.setuptools.packages.find]",
        'where = ["src"]',
        "",
    ])


def fill(template, name, package, version, description):
    return (template.replace("__NAME__", name).replace("__PKG__", package)
            .replace("__VERSION__", version).replace("__DESCRIPTION__", description))


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
