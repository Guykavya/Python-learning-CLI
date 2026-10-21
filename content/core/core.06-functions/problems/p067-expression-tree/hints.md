## Hint 1

What is the base case? How can you tell a number from a tuple? (`isinstance(expr, tuple)`)

## Hint 2

For `(op, left, right)`: trust the recursion to evaluate `left` and `right`, then combine the two results with the function from the dict.

## Hint 3

```
BINARY = {"+": lambda a, b: a + b, "-": lambda a, b: a - b,
          "*": lambda a, b: a * b, "/": lambda a, b: a / b}

def evaluate(expr):
    if not isinstance(expr, tuple): return expr
    if expr[0] == "neg": return -evaluate(expr[1])
    op, left, right = expr
    return BINARY[op](evaluate(left), evaluate(right))
```
