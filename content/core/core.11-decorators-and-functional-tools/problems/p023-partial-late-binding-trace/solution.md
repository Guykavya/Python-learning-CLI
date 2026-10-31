## Approach

- `lambda b: power(b, e)` does not store `e`. It stores the **name**. When called it reads the
  global `e`. After the loop, `e` is 3, so all three give `2 ** 3 = 8`. After `e = 10`,
  `lambdas[0](2)` is `2 ** 10 = 1024`. This is called **late binding**.
- `partial(power, exp=e)` evaluates `e` at once and keeps the value in `.keywords`. So we get
  `[2, 4, 8]`, and changing `e` later has no effect.
- `lambda b, e=e: ...` evaluates the default value when the lambda is made, so it also keeps
  1, 2, 3.
- `partials[0](2, exp=5)`: a keyword passed at call time replaces the stored one: `2 ** 5 = 32`.
- `partial(power, 3)` fixes `base=3`. Calling it with `2` gives `power(3, 2) = 9`.
- A partial object shows what it holds: `.func`, `.args` (a tuple) and `.keywords` (a dict).

## Output

```text
[8, 8, 8]
[2, 4, 8]
[2, 4, 8]
1024
2
2
32
9
power (3,) {}
```

## Complexity

O(1); this is about when values are read.

## Another way

Make the "freeze the value now" rule visible with a small factory:

```python
def make_power(exp):
    return lambda b: power(b, exp)

closures = [make_power(e) for e in range(1, 4)]
```

Each call of `make_power` has its own local `exp`, so each closure keeps its own value. This
is the same idea as `partial`, written by hand.
