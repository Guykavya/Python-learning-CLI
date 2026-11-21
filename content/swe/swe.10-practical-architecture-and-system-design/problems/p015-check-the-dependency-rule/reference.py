import ast

LAYER_RANK = {"domain": 0, "services": 1, "infrastructure": 2, "web": 3}
EXTERNAL_BANS = {
    "domain": {"sqlite3", "fastapi", "httpx", "requests", "smtplib"},
    "services": {"sqlite3", "fastapi", "httpx", "requests", "smtplib"},
}


def _imports(tree, package):
    """Return (project modules, external top-level names) imported anywhere in the tree."""
    project, external = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                parts = alias.name.split(".")
                if parts[0] == package:
                    if len(parts) > 1:
                        project.add(parts[1])
                else:
                    external.add(parts[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level >= 1:                                   # relative: from .x import y / from . import x
                if node.module:
                    project.add(node.module.split(".")[0])
                else:
                    project.update(alias.name for alias in node.names)
            else:
                parts = (node.module or "").split(".")
                if parts[0] == package:
                    if len(parts) > 1:
                        project.add(parts[1])
                    else:
                        project.update(alias.name for alias in node.names)
                else:
                    external.add(parts[0])
    return project, external


def violations(sources, layers, package="taskboard"):
    found = set()
    for module, text in sources.items():
        if module not in layers:
            raise ValueError(f"module {module!r} is not in the layers table")
        my_layer = layers[module]
        project, external = _imports(ast.parse(text), package)
        for imported in project:
            if imported in layers and LAYER_RANK[layers[imported]] > LAYER_RANK[my_layer]:
                found.add((module, imported))
        for library in external:
            if library in EXTERNAL_BANS.get(my_layer, ()):
                found.add((module, library))
    return sorted(found)
