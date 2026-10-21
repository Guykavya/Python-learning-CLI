## Walkthrough

| Expression | Result | Why |
|---|---|---|
| `a and b` | `0` | `a` is falsy, returned at once |
| `b and a` | `0` | `b` is truthy, so the result is `a` |
| `a or b` | `5` | `a` is falsy, so the result is `b` |
| `s or "empty"` | `empty` | empty string is falsy |
| `b > 3 and "big"` | `big` | `True and "big"` gives `"big"` |
| `b > 9 and "big"` | `False` | `False` is returned, `"big"` never looked at |
| `a != 0 and b / a > 1` | `False` | the guard is `False`, the division never runs |
| `not s, not b` | `True False` | `not` always returns a real bool |
| `repr(s and s[0] == "x")` | `''` | `s` is falsy, so `and` returns `s` itself; `s[0]` never runs |
| `b or 1 / a` | `5` | `b` is truthy, the division never runs |
| `None or 0 or "" or "last"` | `last` | the first truthy operand, or the last one |
| `1 and 2 and 3` | `3` | all truthy, so the last operand |
