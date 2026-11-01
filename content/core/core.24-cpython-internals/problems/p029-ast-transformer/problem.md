# Your own constant folder with `ast.NodeTransformer`

Before CPython generates bytecode it **folds constants**: `24 * 60 * 60` is computed once at
compile time, and the code object only stores `86400`. In this problem you write that
optimisation yourself, as a source-to-source tool.

An `ast.NodeTransformer` walks a syntax tree and calls `visit_<NodeType>(node)` for each node.
Whatever the method returns **replaces** the node in the tree (return the node itself to keep it).
`self.generic_visit(node)` visits and replaces the node's children.

Copy `starter.py` to `solution.py` and complete:

**`ConstantFolder(ast.NodeTransformer)`** with a counter `self.folds` (starts at 0). Its
`visit_BinOp` folds a binary operation when:

- the operator is `+`, `-` or `*` (nothing else: not `/`, `//`, `%`, `**`), and
- both operands are **number literals**: an `ast.Constant` whose value's type is exactly `int`
  or `float` (so not `True`, not strings), or a negative literal, which the parser writes as
  `UnaryOp(op=USub(), operand=Constant(3))` for `-3`.

Fold **bottom-up**: first fold the children, then look at the node itself, so
`(1 + 2) * (3 + 4)` becomes `21`. Each replaced `BinOp` adds 1 to `self.folds`.

**A trap to avoid.** If a result is negative, do not return `ast.Constant(-3)`. The parser never
makes such a node, and `ast.unparse` writes it without parentheses: `(1 - 4) ** 2` would come out
as `-3 ** 2`, which Python reads as `-(3 ** 2) = -9`. Build negative results the way the parser
does: `ast.UnaryOp(op=ast.USub(), operand=ast.Constant(3))`. `ast.unparse` then writes `(-3) ** 2`.

**`fold(source)`** parses the source, runs a fresh `ConstantFolder` on it, calls
`ast.fix_missing_locations` on the tree (new nodes need line numbers before they can be
compiled), and returns `(ast.unparse(tree), folder.folds)`.

**Example**

```python
>>> fold("x = 24 * 60 * 60")
('x = 86400', 2)
>>> fold("v = 1 + 2 + x")         # (1 + 2) + x
('v = 3 + x', 1)
>>> fold("u = x + 1 + 2")         # (x + 1) + 2: no BinOp has two literals
('u = x + 1 + 2', 0)
>>> fold("y = (1 - 4) ** 2")      # ** is not folded, but its operand is
('y = (-3) ** 2', 1)
>>> fold("s = True + 1\nt = 'a' + 'b'")
("s = True + 1\nt = 'a' + 'b'", 0)
```
