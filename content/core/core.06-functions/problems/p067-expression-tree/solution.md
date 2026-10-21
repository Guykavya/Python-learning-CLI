## Approach

The data is recursive, so the code is too. A number is the base case. A tuple is either a
negation (one sub-expression) or a binary operation (two sub-expressions); check `"neg"` first,
because it has a different length. Trust the recursive calls for the sub-expressions, then combine
with a function looked up in `BINARY`. `to_text` has exactly the same shape, combining strings
instead of numbers.

## Code

```python
BINARY = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
}


def evaluate(expr):
    """Return the value of a number or a nested (op, left, right) / ('neg', x) tuple."""
    if not isinstance(expr, tuple):
        return expr
    if expr[0] == "neg":
        return -evaluate(expr[1])
    op, left, right = expr
    return BINARY[op](evaluate(left), evaluate(right))


def to_text(expr):
    """Return expr as a fully parenthesised string."""
    if not isinstance(expr, tuple):
        return str(expr)
    if expr[0] == "neg":
        return "-" + to_text(expr[1])
    op, left, right = expr
    return f"({to_text(left)} {op} {to_text(right)})"
```

## Complexity

O(number of nodes) for each function; recursion depth equals the depth of the tree.

## Another way

Put `"neg"` in a second table of one-argument functions, `UNARY = {"neg": lambda a: -a}`, and
choose the table by the tuple's length. Then new operators of either kind need only a table entry.
