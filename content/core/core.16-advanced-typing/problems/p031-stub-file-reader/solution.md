## Approach

`ast.parse` turns source text into a tree without running it. A stub is a list of statements in
`tree.body`: `AnnAssign` for `NAME: type`, `FunctionDef`/`AsyncFunctionDef` for functions and
`ClassDef` for classes (whose own `body` holds the methods). One generator, `_functions`, yields
every function with its qualified name, so the three function-related readers share one walk.

`ast.unparse` turns a node back into source text, which saves rebuilding `/`, `*`, `*args`,
`**kwargs` and defaults by hand. For "untyped" we collect **all** parameters (positional-only,
normal, keyword-only, `*args`, `**kwargs`), drop the first one of a method (`self`/`cls`), and
test whether any annotation, or the return annotation, is missing.

## Code

```python
import ast
from collections.abc import Iterator
from pathlib import Path


def _parse(path: str | Path) -> ast.Module:
    return ast.parse(Path(path).read_text(encoding="utf-8"))


def _functions(tree: ast.Module) -> Iterator[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef, bool]]:
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
            params.remove((a.posonlyargs or a.args)[0])
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
```

## Complexity

O(n) in the size of the stub file (one parse, one walk per function).

## Another way

`ast.walk(tree)` visits every node, but it loses the nesting (you could not tell a method from a
function). Reading the **real** stub through `typing.get_type_hints` is impossible, because stubs
are never imported: they exist only for tools. Tools such as `mypy.stubgen` and `pyright` do
exactly this kind of parsing, with far more care.
