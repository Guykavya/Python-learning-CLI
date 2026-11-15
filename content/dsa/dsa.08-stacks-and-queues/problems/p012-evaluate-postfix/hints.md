## Hint 1

Check for the four operators first: `if t in ("+", "-", "*", "/")`. Everything else, including `"-11"`, is a number and goes through `int(t)`. Which operand comes off the stack first?

## Hint 2

Truncating division without floats: divide the absolute values, then fix the sign.

```
def trunc_div(a, b):
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q
```
