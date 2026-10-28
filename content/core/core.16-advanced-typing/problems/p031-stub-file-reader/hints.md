## Hint 1

What does `ast.parse(text)` give you? Print `tree.body` in the REPL for a tiny stub: which node class is a `def`, which is `X: int`, which is a `class`? Which attribute of a function node holds the parameters, and which holds the return annotation?

## Hint 2

Write one small helper that walks `tree.body` and yields `(qualified name, node, is_method)` for every function and every method, so all four public functions can share it. Then each public function is a short loop. `ast.unparse(node.args)` writes the whole parameter list; `node.returns` is `None` when there is no `->`.

## Hint 3

```
helper functions(tree):
    for node in tree.body:
        FunctionDef/AsyncFunctionDef -> yield node.name, node, False
        ClassDef -> for item in node.body: if a function: yield f"{node.name}.{item.name}", item, True

stub_functions: result.setdefault(name, []).append(signature(node))
signature:      "(" + unparse(args) + ")" + (" -> " + unparse(returns) if returns) ; "async " prefix
stub_untyped:   params = posonlyargs + args + kwonlyargs + vararg + kwarg
                drop the first one for a method; untyped if returns is None or any annotation is None
```
