## Hint 1

`ast.walk(ast.parse(source))` gives you every node. Only two node types matter: `ast.Import` and
`ast.ImportFrom`. For each one, what is the top-level name? How do you tell `from .x import y`
from `from x import y`?

## Hint 2

```text
absolute = set(); relative = set()
for node in ast.walk(ast.parse(source)):
    if node is ast.Import:      for alias in node.names: absolute.add(alias.name.split(".")[0])
    elif node is ast.ImportFrom:
        if node.level == 0:     absolute.add(node.module.split(".")[0])
        else:                   relative.add("." * node.level + (node.module or ""))

classify: groups start as {"stdlib": set(), "third_party": set(), "local": relative}
for name in absolute: local first, then stdlib_module_names, else third_party
return each group sorted
```
