## Hint 1

Print the tree of a small example with `print(ast.dump(ast.parse(src), indent=2))`. Which node
types hold imports (`ast.Import`, `ast.ImportFrom`), which hold `except` clauses, and where do a
function's default values live (`node.args.defaults`, `node.args.kw_defaults`)? For unused
imports you need two passes: first collect every name that is read, then check each imported
name against that set.

## Hint 2

```
try: tree = ast.parse(source)
except SyntaxError as e: return [(e.lineno, "E999")]
used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
for node in ast.walk(tree):
    Import:      for alias in node.names: bound = alias.asname or alias.name.split(".")[0]
    ImportFrom:  skip __future__ and "*"; bound = alias.asname or alias.name
                 if bound not in used: add (node.lineno, "F401")
    ExceptHandler with node.type is None: add (node.lineno, "E722")
    FunctionDef / AsyncFunctionDef / Lambda:
        for d in node.args.defaults + [d for d in node.args.kw_defaults if d is not None]:
            if d is List/Dict/Set, or Call whose func is Name list/dict/set: add (d.lineno, "B006")
return sorted(issues)
```
