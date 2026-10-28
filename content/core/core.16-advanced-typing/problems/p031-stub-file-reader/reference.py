import ast
from collections.abc import Iterator
from pathlib import Path


def _parse(path: str | Path) -> ast.Module:
    return ast.parse(Path(path).read_text(encoding="utf-8"))


def _functions(tree: ast.Module) -> Iterator[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef, bool]]:
    """Yield (qualified name, node, is_method) in file order."""
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node.name, node, False
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    yield f"{node.name}.{item.name}", item, True


def _signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    text = f"({ast.unparse(node.args)})"
    if node.returns is not None:
        text += f" -> {ast.unparse(node.returns)}"
    if isinstance(node, ast.AsyncFunctionDef):
        text = "async " + text
    return text


def stub_variables(path: str | Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for node in _parse(path).body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            result[node.target.id] = ast.unparse(node.annotation)
    return result


def stub_functions(path: str | Path) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for name, node, _ in _functions(_parse(path)):
        result.setdefault(name, []).append(_signature(node))
    return result


def stub_untyped(path: str | Path) -> list[str]:
    result: list[str] = []
    for name, node, is_method in _functions(_parse(path)):
        a = node.args
        params = [*a.posonlyargs, *a.args, *a.kwonlyargs]
        if a.vararg:
            params.append(a.vararg)
        if a.kwarg:
            params.append(a.kwarg)
        if is_method and (a.posonlyargs or a.args):
            first = (a.posonlyargs or a.args)[0]
            params.remove(first)
        if node.returns is None or any(p.annotation is None for p in params):
            if name not in result:
                result.append(name)
    return result


def stub_classes(path: str | Path) -> dict[str, list[str]]:
    return {
        node.name: [ast.unparse(b) for b in node.bases]
        for node in _parse(path).body
        if isinstance(node, ast.ClassDef)
    }
