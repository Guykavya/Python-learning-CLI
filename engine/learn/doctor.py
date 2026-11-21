"""doctor: what does this machine have, and what does a module need that it does not?

It reads the code blocks of a chapter, finds every package they import, and compares that with what is installed and with the
packages listed in pyproject.toml (base packages and optional groups such as 'ml' and 'llm')."""

from __future__ import annotations

import ast
import importlib.metadata as md
import importlib.util
import re
import shutil
import sqlite3
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from learn import chapters, config, paths

# import name -> name of the package you pip install (only where they differ)
ALIASES = {"sklearn": "scikit-learn", "PIL": "pillow", "yaml": "pyyaml", "bs4": "beautifulsoup4", "cv2": "opencv-python", "jwt": "pyjwt",
           "multipart": "python-multipart", "dotenv": "python-dotenv", "skimage": "scikit-image", "attr": "attrs", "dateutil": "python-dateutil",
           "rest_framework": "djangorestframework", "flask_sqlalchemy": "flask-sqlalchemy", "git": "gitpython", "google": "protobuf",
           "onnxruntime": "onnxruntime", "jupyterlab": "jupyterlab", "nbformat": "nbformat", "pytest_asyncio": "pytest-asyncio", "umap": "umap-learn",
           "bokeh": "bokeh", "dateparser": "dateparser"}
SIZE_HINT = {"torch": "about 2 GB", "torchvision": "about 1 GB", "transformers": "hundreds of MB", "datasets": "tens of MB", "onnxruntime": "tens of MB",
             "mlflow": "hundreds of MB", "dvc": "hundreds of MB", "jupyterlab": "hundreds of MB", "streamlit": "tens of MB", "shap": "tens of MB"}
IGNORE = {"learn", "solution", "conftest", "app", "main", "test", "tests"}          # modules a chapter or a problem creates itself


def norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


@dataclass
class Requirements:
    base: dict[str, str] = field(default_factory=dict)             # normalised name -> original spec
    extras: dict[str, dict[str, str]] = field(default_factory=dict)  # group -> {normalised name: spec}

    def group_of(self, dist: str) -> str | None:
        d = norm(dist)
        if d in self.base:
            return "base"
        for group, pkgs in self.extras.items():
            if d in pkgs:
                return group
        return None


def load_requirements(pyproject: Path | None = None) -> Requirements:
    data = tomllib.loads((pyproject or paths.root() / "pyproject.toml").read_text(encoding="utf-8"))
    def names(specs):
        return {norm(re.split(r"[\s\[<>=!~;]", s, maxsplit=1)[0]): s for s in specs}
    return Requirements(names(data["project"].get("dependencies", [])), {g: names(s) for g, s in data["project"].get("optional-dependencies", {}).items()})


def is_installed(dist: str) -> bool:
    try:
        md.version(dist)
        return True
    except md.PackageNotFoundError:
        return False


def imports_of(code: str) -> list[tuple[str, bool]]:
    """(top-level module name, optional?) for every import. An import inside try/except is optional (the code copes without it)."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    found: list[tuple[str, bool]] = []

    def visit(node: ast.AST, optional: bool) -> None:
        if isinstance(node, ast.Import):
            found.extend((a.name.split(".")[0], optional) for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            found.append((node.module.split(".")[0], optional))
        for child in ast.iter_child_nodes(node):
            visit(child, optional or (isinstance(node, ast.Try) and child in node.body))
    visit(tree, False)
    return found


@dataclass
class ChapterNeeds:
    installed: list[str] = field(default_factory=list)
    missing: dict[str, str] = field(default_factory=dict)          # package -> group ('base', 'ml', ...)
    optional_missing: list[str] = field(default_factory=list)
    undeclared: list[str] = field(default_factory=list)            # imported, not stdlib, not local, not in pyproject


def chapter_needs(text: str, req: Requirements) -> ChapterNeeds:
    needs = ChapterNeeds()
    local = {Path(f.relpath).stem for f in chapters.extract_files(text) if f.relpath.endswith(".py")}
    seen: dict[str, bool] = {}
    for b in chapters.parse_blocks(text)[0]:
        if b.is_python_run:                                      # only code the chapter actually ran; 'try it on your machine' snippets are not requirements
            for name, optional in imports_of(b.code):
                seen[name] = seen.get(name, True) and optional          # required if it is required anywhere
    for name, optional in sorted(seen.items()):
        if name in sys.stdlib_module_names or name in local or name in IGNORE or name.startswith("_"):
            continue
        if re.search(rf"\b{re.escape(name)}(\.py\b|/)", text):       # a module or package the chapter builds (named as a file or folder in the text)
            continue
        dist = ALIASES.get(name, name)
        group = req.group_of(dist)
        present = importlib.util.find_spec(name) is not None
        if present:
            needs.installed.append(name)
        elif group is None:
            needs.undeclared.append(name)
        elif optional:
            needs.optional_missing.append(dist)
        else:
            needs.missing[dist] = group
    return needs


def environment_report() -> list[tuple[str, str, str]]:
    """(label, status 'ok' | 'warn' | 'bad', detail) for the machine itself."""
    rows = []
    v = sys.version_info
    rows.append(("Python", "ok" if v >= (3, 11) else "bad", f"{v.major}.{v.minor}.{v.micro} on {sys.platform}" + ("" if v >= (3, 11) else " (3.11 or newer needed)")))
    utf8 = bool(sys.flags.utf8_mode)
    if sys.platform == "win32" and v < (3, 15) and not utf8:
        rows.append(("UTF-8 mode", "warn", "off. Chapter code that writes text files may fail on non-ASCII text. The ./learn launcher turns it on; "
                     "in your own terminal run:  $env:PYTHONUTF8 = '1'  (PowerShell)  or  set PYTHONUTF8=1  (CMD)"))
    else:
        rows.append(("UTF-8 mode", "ok", "on" if utf8 else "off (fine on this system)"))
    rows.append(("git", "ok" if shutil.which("git") else "warn", "found" if shutil.which("git") else "not found (optional: progress history and downloads)"))
    tui_wanted = config.load().get("ui", {}).get("mode", "plain") == "tui"
    has_textual = importlib.util.find_spec("textual") is not None
    if has_textual:
        rows.append(("Full-screen mode", "ok", "Textual installed" + ("" if tui_wanted else " (mode is plain: learn config set ui.mode tui)")))
    elif tui_wanted:
        rows.append(("Full-screen mode", "warn", 'ui.mode is "tui" but Textual is missing, so learn stays plain. Fix: learn config set ui.mode tui'))
    else:
        rows.append(("Full-screen mode", "ok", "optional, not installed. Turn on with: learn config set ui.mode tui"))
    try:
        con = sqlite3.connect(":memory:")
        con.execute("CREATE VIRTUAL TABLE t USING fts5(x)")
        rows.append(("SQLite full-text (FTS5)", "ok", f"SQLite {sqlite3.sqlite_version} (needed by llm.03)"))
    except sqlite3.OperationalError:
        rows.append(("SQLite full-text (FTS5)", "warn", "missing in this Python's SQLite (llm.03 needs it)"))
    return rows


def group_status(req: Requirements) -> list[tuple[str, int, int]]:
    out = [("base", sum(is_installed(n) for n in req.base), len(req.base))]
    out += [(g, sum(is_installed(n) for n in pk), len(pk)) for g, pk in req.extras.items()]
    return out
