## Walkthrough

| Line | Output | Why |
|---|---|---|
| `1 < x < 10` | `True` | 1 < 5 and 5 < 10 |
| `1 < x > 3` | `True` | 1 < 5 and 5 > 3 |
| `10 > x < 3` | `False` | 10 > 5 is True, but 5 < 3 is False |
| `x == 5 == 5.0` | `True` | 5 == 5 and 5 == 5.0 |
| `0 < x != 5` | `False` | 0 < 5 is True, 5 != 5 is False |
| `3 < x < 4 or x` | `5` | the chain is False, so `or` returns `x` |
| `x > 0 and x * 2` | `10` | first part truthy, so `and` returns the second operand |
| `0 and 1 / 0` | `0` | `0` is falsy; `and` returns it and never divides |
| `x or 1 / 0` | `5` | `5` is truthy; `or` returns it and never divides |
| `(x := 7) > 5, x` | `True 7` | the walrus binds `x` to 7 first, then compares |
| `x - 7 or "zero"` | `zero` | `7 - 7` is `0`, falsy, so `or` returns `"zero"` |

## The rule

Chains are an `and` of neighbouring pairs, each middle value evaluated once. `and`/`or` return an
operand, and they skip the right side when the left side already decides the answer.
