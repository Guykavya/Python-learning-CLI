## Approach

Choose each varying part with a conditional expression, then join the parts.

## Code

```python
n = int(input())
noun = input().strip()
amount = "no" if n == 0 else str(n)
ending = "" if n == 1 else "s"
print(f"{amount} {noun}{ending}")
```

## Why conditional expressions

The two branches differ only in a **value**, not in what the program does. A conditional
expression says that directly. With `if` statements you would repeat the `print` three times.

## Another way

One chained expression: `print(f"no {noun}s" if n == 0 else f"1 {noun}" if n == 1 else f"{n} {noun}s")`.
It works, but chains longer than two choices are harder to read.
