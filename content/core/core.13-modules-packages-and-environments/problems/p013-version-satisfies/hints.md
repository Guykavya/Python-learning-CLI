## Hint 1

Split the work into three small functions: turn `"1.10.2"` into `(1, 10, 2)`; split one clause like
`">= 1.2"` into `(">=", "1.2")`; compare two tuples with one operator. Why must you test for `">="`
**before** `">"` when you look at the start of a clause?

## Hint 2

Python compares tuples item by item, like words in a dictionary: `(1, 10) > (1, 9)` is `True`.
To pad: `n = max(len(a), len(b))`, then `a + (0,) * (n - len(a))`.

## Hint 3

```
def satisfies(version, spec):
    v = to_tuple(version)
    for clause in spec.split(","):
        clause = clause.strip()
        if clause == "": continue
        for op in ("==", "!=", ">=", "<=", ">", "<"):
            if clause.startswith(op): break
        else: raise ValueError(...)
        rest = clause[len(op):].strip()
        if rest is empty or starts with "=": raise ValueError(...)
        a, b = pad(v, to_tuple(rest))
        if not compare(a, op, b): return False
    return True
```
