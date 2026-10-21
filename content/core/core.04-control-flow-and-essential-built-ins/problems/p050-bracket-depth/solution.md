## Approach

A depth counter per line. The first time it goes negative, report and stop that line (early
exit). If the loop finishes, the final depth tells you whether anything is left open.

## Code

```python
n = int(input())
balanced = 0
for _ in range(n):
    line = input()
    depth = 0
    deepest = 0
    for pos, ch in enumerate(line):
        if ch == "(":
            depth += 1
            deepest = max(deepest, depth)
        elif ch == ")":
            depth -= 1
            if depth < 0:
                print(f"Unbalanced: unexpected ')' at position {pos}")
                break
    else:
        if depth > 0:
            print(f"Unbalanced: {depth} unclosed '('")
        else:
            print(f"Balanced, max depth {deepest}")
            balanced += 1
print(f"Balanced: {balanced} of {n}")
```

## Why the early exit matters for correctness

For `)(`, the final depth is 0, which looks balanced. Only by stopping when the depth first
goes negative do you catch that the `)` came before its `(`. The order of events matters, not
just the totals.

## Why the loop `else`

The final checks should only run when the loop was **not** stopped by `break`. That is
exactly what a loop `else` means.

## Limits

One counter is enough for a single kind of bracket. With `()`, `[]` and `{}` mixed, you must
remember the order of open brackets, which needs a stack (a list), from later chapters.
