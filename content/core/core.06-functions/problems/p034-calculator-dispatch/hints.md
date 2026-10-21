## Hint 1

How do you store a function in a dict without calling it?

## Hint 2

`func = OPERATIONS.get(op)` gives the function or `None`. If it is `None`, return `None`; otherwise call it.

## Hint 3

```
OPERATIONS = {"+": add, "-": subtract, "*": multiply, "/": divide}

def calculate(a, op, b):
    func = OPERATIONS.get(op)
    if func is None:
        return None
    return func(a, b)
```
