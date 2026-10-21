## Hint 1

Look at the tree in chapter section 4. Which class is the parent of both `KeyError` and
`IndexError`? Of `ZeroDivisionError` and `OverflowError`?

## Hint 2

Four `except` clauses, each returning a word. The `"ok"` return goes after the `try` statement
(or in an `else` block).

## Hint 3

```
try:
    func(*args)
except LookupError:
    return "lookup"
except ArithmeticError:
    return "arithmetic"
... ValueError, TypeError ...
return "ok"
```
