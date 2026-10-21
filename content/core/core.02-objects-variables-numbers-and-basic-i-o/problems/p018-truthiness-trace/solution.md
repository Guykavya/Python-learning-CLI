## Walkthrough

| Expression | Result | Why |
|---|---|---|
| `bool(0)` | `False` | zero is falsy |
| `bool(-1)` | `True` | any non-zero number is truthy, negatives too |
| `bool(0.0)` | `False` | float zero |
| `bool(0.1)` | `True` | non-zero |
| `bool("")` | `False` | empty string |
| `bool(" ")` | `True` | a space is a character, so the string is not empty |
| `bool("0")` | `True` | non-empty string; Python does not read its meaning |
| `bool("False")` | `True` | same reason |
| `bool(None)` | `False` | `None` is always falsy |
| `bool(0j)` | `False` | complex zero |
| `0 or 7` | `7` | `0` is falsy, so `or` returns the second operand |
| `3 and "yes"` | `yes` | `3` is truthy, so `and` returns the second operand |
| `None or 0.0` | `0.0` | `None` is falsy, so `or` returns `0.0`, even though it is also falsy |

## The rule

Falsy values: `False`, `None`, zero of any numeric type, and empty containers or strings.
Everything else is truthy.
