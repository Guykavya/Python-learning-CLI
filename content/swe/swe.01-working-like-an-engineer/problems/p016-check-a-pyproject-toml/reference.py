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
