## Approach

Parse once with `ast.parse`, then:

1. **Collect the names that are read.** Every `ast.Name` node with a `Load` context, anywhere in
   the module. `os.path.join(x)` is an `Attribute` chain whose root is `Name(id='os')`, so it is
   collected too.
2. **Walk the tree** and look at three node types:
   - `Import` / `ImportFrom`: for each alias work out the **bound** name (the alias, or the first
     part of a dotted module name) and report it if it is not in the set from step 1.
   - `ExceptHandler` with `type is None`: a bare `except:`.
   - `FunctionDef`, `AsyncFunctionDef`, `Lambda`: check `args.defaults` and `args.kw_defaults`
     (the latter contains `None` for keyword-only parameters with no default).
3. Sort the list of tuples; tuples sort by line first, then by code.

A syntax error means there is no tree; return `E999` at the line Python reports.

## Code

```python
import ast

MUTABLE_CALLS = {"list", "dict", "set"}


def is_mutable_default(node):
    if isinstance(node, (ast.List, ast.Dict, ast.Set)):
        return True
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in MUTABLE_CALLS


def find_issues(source):
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        return [(error.lineno or 1, "E999")]
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if (alias.asname or alias.name.split(".")[0]) not in used:
                    issues.append((node.lineno, "F401"))
        elif isinstance(node, ast.ImportFrom):
            if node.module == "__future__":
                continue
            for alias in node.names:
                if alias.name != "*" and (alias.asname or alias.name) not in used:
                    issues.append((node.lineno, "F401"))
        elif isinstance(node, ast.ExceptHandler) and node.type is None:
            issues.append((node.lineno, "E722"))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            for default in node.args.defaults + [d for d in node.args.kw_defaults if d is not None]:
                if is_mutable_default(default):
                    issues.append((default.lineno, "B006"))
    return sorted(issues)
```

## Complexity

Two walks over the tree: O(number of nodes), plus O(k log k) to sort k issues.

## Another way

Subclass `ast.NodeVisitor` and write `visit_Import`, `visit_ExceptHandler`,
`visit_FunctionDef`, ... methods (remember to call `self.generic_visit(node)` so children are
visited). That is how real linters are organised: one small visitor method per rule. Real
`ruff` is also smarter about scope: it knows that a name read in one function does not "use"
an import that was shadowed there, and it treats names listed in `__all__` as used.
