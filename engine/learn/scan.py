"""Observe the playground folder. Nothing there is graded; the scan only notices
which Python features and libraries you practised on your own.
"""

from __future__ import annotations

import ast
import hashlib
import sqlite3
from pathlib import Path

from learn import db, paths

IMPORT_MODULES = {
    "re": "core.18", "pathlib": "core.12", "os": "core.12", "shutil": "core.12", "csv": "core.12",
    "json": "core.12", "argparse": "core.12", "tomllib": "core.12",
    "itertools": "core.10", "functools": "core.11",
    "collections": "core.17", "heapq": "core.17", "bisect": "core.17", "datetime": "core.17",
    "zoneinfo": "core.17", "logging": "core.17", "subprocess": "core.17", "random": "core.17",
    "statistics": "core.17", "hashlib": "core.17",
    "typing": "core.09", "dataclasses": "core.15", "enum": "core.15", "contextlib": "core.15", "abc": "core.14",
    "threading": "core.21", "multiprocessing": "core.21", "asyncio": "core.21", "concurrent": "core.21",
    "unittest": "core.19", "pytest": "core.08", "hypothesis": "core.19",
    "dis": "core.24", "ctypes": "core.24",
    "sqlite3": "shared.01", "httpx": "swe.02", "requests": "swe.02", "socket": "swe.02",
    "bs4": "swe.02", "sqlalchemy": "swe.03", "psycopg": "swe.03", "pymysql": "swe.03",
    "flask": "swe.04", "fastapi": "swe.05", "pydantic": "swe.05", "django": "swe.06",
    "redis": "swe.08", "celery": "swe.08", "typer": "swe.11", "click": "swe.11", "playwright": "swe.11",
    "numpy": "da.02", "pandas": "da.03", "polars": "da.04", "matplotlib": "da.09", "seaborn": "da.09",
    "plotly": "da.09", "streamlit": "da.10", "openpyxl": "da.12", "duckdb": "da.07",
    "scipy": "ds.01", "statsmodels": "ds.02", "sklearn": "ds.05", "xgboost": "ds.06", "lightgbm": "ds.06",
    "torch": "ml.02", "torchvision": "ml.03", "transformers": "ml.05", "mlflow": "ml.06",
    "anthropic": "llm.02", "openai": "llm.02",
}

FEATURE_MODULES = {
    "f-string": "core.03", "loop": "core.04", "match-case": "core.04",
    "comprehension": "core.05", "function": "core.06", "lambda": "core.06",
    "closure": "core.06", "recursion": "core.06", "try-except": "core.07",
    "raise": "core.07", "pytest-test": "core.08", "type-hints": "core.09",
    "generator": "core.10", "decorator": "core.11", "with": "core.12",
    "class": "core.14", "inheritance": "core.14", "dunder-methods": "core.15",
    "dataclass": "core.15", "async": "core.21",
}


def features_of(source: str) -> set[str]:
    tree = ast.parse(source)
    found: set[str] = set()
    func_names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            found.add("f-string")
        elif isinstance(node, (ast.For, ast.While)):
            found.add("loop")
        elif isinstance(node, ast.Match):
            found.add("match-case")
        elif isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
            found.add("comprehension")
        elif isinstance(node, ast.Lambda):
            found.add("lambda")
        elif isinstance(node, (ast.Try, getattr(ast, "TryStar", ast.Try))):
            found.add("try-except")
        elif isinstance(node, ast.Raise):
            found.add("raise")
        elif isinstance(node, (ast.Yield, ast.YieldFrom)):
            found.add("generator")
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            found.add("with")
        elif isinstance(node, (ast.AsyncFunctionDef, ast.Await)):
            found.add("async")
        elif isinstance(node, ast.ClassDef):
            found.add("class")
            if node.bases:
                found.add("inheritance")
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name.startswith("__") and item.name != "__init__":
                    found.add("dunder-methods")
            for d in node.decorator_list:
                if "dataclass" in ast.unparse(d):
                    found.add("dataclass")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            found.add("function")
            func_names.append(node.name)
            if node.name.startswith("test_"):
                found.add("pytest-test")
            if node.returns or any(a.annotation for a in node.args.args):
                found.add("type-hints")
            if node.decorator_list:
                found.add("decorator")
            for inner in ast.walk(node):
                if inner is not node and isinstance(inner, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    found.add("closure")
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name) and inner.func.id == node.name:
                    found.add("recursion")
        if isinstance(node, ast.AnnAssign):
            found.add("type-hints")
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add("import:" + alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.add("import:" + node.module.split(".")[0])
    return found


def modules_of(features: set[str]) -> set[str]:
    mods = set()
    for f in features:
        if f.startswith("import:"):
            m = IMPORT_MODULES.get(f[7:])
        else:
            m = FEATURE_MODULES.get(f)
        if m:
            mods.add(m)
    return mods


def scan(conn: sqlite3.Connection) -> int:
    """Scan changed .py files in the playground. Returns how many changed files were found."""
    base = paths.playground_dir()
    if not base.exists():
        return 0
    known = {r["path"]: r["hash"] for r in conn.execute("SELECT path, hash FROM playground_files")}
    changed = 0
    for f in base.rglob("*.py"):
        if any(part.startswith(".") or part in ("__pycache__", "venv", ".venv") for part in f.parts):
            continue
        rel = str(f.relative_to(base))
        try:
            raw = f.read_bytes()
        except OSError:
            continue
        digest = hashlib.sha1(raw).hexdigest()
        if known.get(rel) == digest:
            continue
        try:
            feats = features_of(raw.decode("utf-8", errors="replace"))
        except SyntaxError:
            continue  # half-written file; it will be scanned once it parses
        mods = modules_of(feats)
        conn.execute(
            "INSERT INTO playground_files(path, hash, scanned_at, features, modules) VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(path) DO UPDATE SET hash = excluded.hash, scanned_at = excluded.scanned_at, "
            "features = excluded.features, modules = excluded.modules",
            (rel, digest, db.now(), ",".join(sorted(feats)), ",".join(sorted(mods))),
        )
        for m in mods:
            conn.execute(
                "INSERT INTO playground_activity(day, module_id, files) VALUES (?, ?, 1) "
                "ON CONFLICT(day, module_id) DO UPDATE SET files = files + 1",
                (db.today(), m),
            )
        changed += 1
    if changed:
        db.mark_active(conn)
    return changed


def self_practice(conn: sqlite3.Connection) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in conn.execute("SELECT modules FROM playground_files"):
        for m in filter(None, row[0].split(",")):
            out[m] = out.get(m, 0) + 1
    return out
