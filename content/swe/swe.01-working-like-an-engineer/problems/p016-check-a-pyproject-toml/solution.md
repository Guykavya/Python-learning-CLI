## Approach

```python
import re
import tomllib

_BOUND = re.compile(r"(>=|==|~=|===|>)\s*\d")


def check_pyproject(text, files):
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return ["invalid TOML"]
    problems = []
    project = data.get("project", {})
    if "name" not in project:
        problems.append("missing project.name")
    if "version" not in project and "version" not in project.get("dynamic", []):
        problems.append("missing project.version")
    if "requires-python" not in project:
        problems.append("missing project.requires-python")
    if not any(re.fullmatch(r"src/[^/]+/__init__\.py", f) for f in files):
        problems.append("no package under src/")
    tool = data.get("tool", {})
    testpaths = tool.get("pytest", {}).get("ini_options", {}).get("testpaths", [])
    for entry in testpaths:
        folder = entry.rstrip("/") + "/"
        if not any(f.startswith(folder) for f in files):
            problems.append(f"testpaths folder missing: {entry}")
    if "ruff" in tool and any(f in ("ruff.toml", ".ruff.toml") for f in files):
        problems.append("ruff is configured twice (pyproject.toml and ruff.toml)")
    deps = list(project.get("dependencies", []))
    for group in project.get("optional-dependencies", {}).values():
        deps.extend(group)
    for dep in deps:
        if not _BOUND.search(dep):
            problems.append(f"dependency without a lower bound: {dep}")
    return problems
```

Each check reads one fact from the parsed dictionary or the file list. Using `.get(..., default)` everywhere means a missing section (no `[tool]`, no `[project]`) never crashes: it just produces the matching problem message.

Example: `'[project]\nname = "x"\n'` has a name, so there is no `missing project.name`; it lacks a version and `requires-python`; and the file list has no `src/<pkg>/__init__.py`. The result is the three messages of the statement, in table order.

## Complexity

`O(size of the file + number of files * number of checks)`.

## Another way

For real projects use `validate-pyproject` or let `pip install -e .` fail. This function shows how little code a useful project check needs, and it is the kind of check you can add to a pre-commit hook (chapter section 14).

## Why it matters

A missing `requires-python` or an unpinned dependency does not break your machine today; it breaks someone else's install next month. Checks like this find it before then.
