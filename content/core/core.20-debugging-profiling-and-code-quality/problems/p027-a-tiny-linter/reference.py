import ast

MUTABLE_CALLS = {"list", "dict", "set"}


def is_mutable_default(node):
    if isinstance(node, (ast.List, ast.Dict, ast.Set)):
        return True
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in MUTABLE_CALLS
    )


def find_issues(source):
    """Return sorted (line, code) pairs for F401, E722 and B006 problems in the source."""
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        return [(error.lineno or 1, "E999")]

    used = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                bound = alias.asname or alias.name.split(".")[0]
                if bound not in used:
                    issues.append((node.lineno, "F401"))
        elif isinstance(node, ast.ImportFrom):
            if node.module == "__future__":
                continue
            for alias in node.names:
                if alias.name == "*":
                    continue
                bound = alias.asname or alias.name
                if bound not in used:
                    issues.append((node.lineno, "F401"))
        elif isinstance(node, ast.ExceptHandler) and node.type is None:
            issues.append((node.lineno, "E722"))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            defaults = node.args.defaults + [d for d in node.args.kw_defaults if d is not None]
            for default in defaults:
                if is_mutable_default(default):
                    issues.append((default.lineno, "B006"))
    return sorted(issues)
