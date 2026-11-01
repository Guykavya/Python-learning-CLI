## Hint 1

When `visit_BinOp` is called for `(1 + 2) * 3`, its left child is still a `BinOp`. What must
happen *before* you test whether both sides are literals? Which `NodeTransformer` method visits
and replaces the children for you?

How do you recognise a number literal? Why is `isinstance(node.value, int)` not enough? (Try
`isinstance(True, int)`.) What does `ast.dump(ast.parse("-3", mode="eval"))` show: is `-3` one
node or two?

## Hint 2

```
number_value(node):
    Constant with type(value) in (int, float)            -> value
    UnaryOp(USub) around such a Constant                 -> -value
    anything else                                        -> None

make_number(value):
    value < 0 -> UnaryOp(op=USub(), operand=Constant(-value))
    else      -> Constant(value)

visit_BinOp(node):
    self.generic_visit(node)                  # children first
    op = {Add: +, Sub: -, Mult: *}.get(type(node.op))
    a, b = number_value(node.left), number_value(node.right)
    if op is None or a is None or b is None: return node
    self.folds += 1
    return ast.copy_location(make_number(op(a, b)), node)
```

Compare `a is None`, not `not a`: the literal `0` is a perfectly good number.
