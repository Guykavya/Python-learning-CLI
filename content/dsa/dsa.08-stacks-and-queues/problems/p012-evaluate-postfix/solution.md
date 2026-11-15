## Approach

The stack holds the values computed so far. A number is pushed; an operator pops its two operands (right one first), applies itself and pushes the result. Postfix needs no precedence rules: the token order is the order of the work.

## Code

```python
def trunc_div(a, b):
    """Integer division that rounds toward zero."""
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


def eval_rpn(tokens):
    stack = []
    for t in tokens:
        if t in ("+", "-", "*", "/"):
            b = stack.pop()              # right operand comes off first
            a = stack.pop()
            if t == "+":
                stack.append(a + b)
            elif t == "-":
                stack.append(a - b)
            elif t == "*":
                stack.append(a * b)
            else:
                stack.append(trunc_div(a, b))
        else:
            stack.append(int(t))
    return stack[0]
```

## Complexity

`O(n)` time for `n` tokens, `O(n)` memory for the stack.

## Another way

A dictionary of small functions (or `operator.add`, `operator.sub`, ...) replaces the `if` chain:

```python
OPS = {"+": lambda a, b: a + b, "-": lambda a, b: a - b,
       "*": lambda a, b: a * b, "/": trunc_div}
...
if t in OPS:
    b = stack.pop(); a = stack.pop()
    stack.append(OPS[t](a, b))
```
