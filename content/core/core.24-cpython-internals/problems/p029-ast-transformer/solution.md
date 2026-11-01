## Approach

A `NodeTransformer` replaces each node with whatever its `visit_...` method returns. Folding must
be **bottom-up**: `generic_visit(node)` first replaces the children (so nested literal expressions
are already single literals), then the node itself is checked. Two helpers keep the rule clear:
`number_value` reads a number literal in both shapes the parser produces (`Constant(3)` and
`UnaryOp(USub, Constant(3))`), and `make_number` writes a number back in those same shapes, which
is what keeps `ast.unparse`'s parentheses right for negative results.

## Code

```python
"""A constant folder: an ast.NodeTransformer that computes + - * on number literals."""

import ast

OPERATORS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
}


def number_value(node):
    """The value of a number literal (int or float, not bool), also written as -literal; else None."""
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if (isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub)
            and isinstance(node.operand, ast.Constant) and type(node.operand.value) in (int, float)):
        return -node.operand.value
    return None


def make_number(value):
    """A node for value. Negative numbers become -(positive literal), exactly as the parser makes them."""
    if value < 0:
        return ast.UnaryOp(op=ast.USub(), operand=ast.Constant(-value))
    return ast.Constant(value)


class ConstantFolder(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.folds = 0

    def visit_BinOp(self, node):
        self.generic_visit(node)  # fold the children first (bottom-up)
        operator = OPERATORS.get(type(node.op))
        left, right = number_value(node.left), number_value(node.right)
        if operator is None or left is None or right is None:
            return node
        self.folds += 1
        return ast.copy_location(make_number(operator(left, right)), node)


def fold(source):
    """Return (new_source, number_of_folds)."""
    tree = ast.parse(source)
    folder = ConstantFolder()
    tree = folder.visit(tree)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree), folder.folds
```

`ast.copy_location(new, node)` gives the new node the old node's line and column, so error
messages and tracebacks would still point at the right place; `fix_missing_locations` then fills
in the `UnaryOp`'s inner `Constant`.

**CPython does this too**, but in C: before Python 3.14 the AST optimiser (`Python/ast_opt.c`)
folds constants in the tree, exactly like this exercise; since 3.14 most of it happens a step later,
on the instruction sequence. Either way, `dis` shows `LOAD_CONST 86400` for `24 * 60 * 60`.
CPython is careful about size: it refuses to fold results that would be huge (for example a
string or tuple longer than a limit, or an enormous power) so that `.pyc` files stay small.

## Complexity

O(N) for N nodes: every node is visited once, and each fold is O(1) for small numbers (big-integer
multiplication grows with the number of digits).

## Another way

Let the parser build the result node for you: `ast.parse(repr(value), mode="eval").body` returns
`Constant(5)` for 5 and `UnaryOp(USub, Constant(3))` for -3, exactly the parser's shapes. And
`ast.literal_eval(node)` can read a literal node (including `-3`) safely:

```python
def visit_BinOp(self, node):
    self.generic_visit(node)
    if type(node.op) in OPS:
        try:
            a, b = ast.literal_eval(node.left), ast.literal_eval(node.right)
        except ValueError:
            return node
        if type(a) in (int, float) and type(b) in (int, float):
            self.folds += 1
            new = ast.parse(repr(OPS[type(node.op)](a, b)), mode="eval").body
            return ast.copy_location(new, node)
    return node
```

Careful: `literal_eval` also accepts lists, tuples and strings, so the `type(...)` check is still
needed.
