# A first look at the AST

Before Python compiles your code to bytecode, the parser turns the text into an **abstract
syntax tree** (AST): a tree of node objects such as `Assign`, `BinOp`, `Name` and `Constant`.
The `ast` module gives you that tree:

- `ast.parse(source)` returns the root, always an `ast.Module` node.
- `ast.walk(tree)` yields **every** node in the tree (the root included), in no particular order
  you should rely on.
- `type(node).__name__` is the node's type name, for example `"BinOp"`.
- A variable used in code is an `ast.Name` node; its `.id` is the variable name. An attribute
  such as `obj.total` is an `ast.Attribute` node (its name is in `.attr`), and a function
  parameter is an `ast.arg` node.

Copy `starter.py` to `solution.py` and write two functions.

**`count_nodes(source)`** returns a `collections.Counter` mapping node type names to how many
nodes of that type the tree contains. Invalid source must raise `SyntaxError` (just let
`ast.parse` raise it).

**`uses_name(source, name)`** returns `True` if `name` appears anywhere in the tree as an
`ast.Name` node (read or assigned), otherwise `False`. Text inside strings, attribute names and
parameter names do not count.

**Example**

```python
counts = count_nodes("x = 1 + 2")
counts["Constant"]    # 2
counts["BinOp"]       # 1
counts["Module"]      # 1
counts["Call"]        # 0   (a Counter gives 0 for missing keys)

uses_name("print(total)", "total")      # True
uses_name("obj.total = 5", "total")     # False: total is an attribute here
uses_name("print('total')", "total")    # False: only text in a string
```

`ast.walk` also yields small helper nodes such as `Load`, `Store` and `Add`. They are counted
like any other node; the tests do not check them because they are not interesting.
