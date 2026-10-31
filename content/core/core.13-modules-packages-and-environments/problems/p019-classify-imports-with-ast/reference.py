import ast
import sys


def _absolute_and_relative(source):
    """Return (set of top-level absolute names, set of relative import strings)."""
    absolute = set()
    relative = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                absolute.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                absolute.add(node.module.split(".")[0])
            else:
                relative.add("." * node.level + (node.module or ""))
    return absolute, relative


def find_imports(source):
    absolute, _relative = _absolute_and_relative(source)
    return sorted(absolute)


def classify_imports(source, local=()):
    absolute, relative = _absolute_and_relative(source)
    local = set(local)
    groups = {"stdlib": set(), "third_party": set(), "local": set(relative)}
    for name in absolute:
        if name in local:
            groups["local"].add(name)
        elif name in sys.stdlib_module_names:
            groups["stdlib"].add(name)
        else:
            groups["third_party"].add(name)
    return {key: sorted(names) for key, names in groups.items()}
