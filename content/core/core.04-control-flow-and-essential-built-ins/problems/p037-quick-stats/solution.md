## Approach

Let the built-ins do the loops. `default=None` handles the empty line for `min` and `max`;
`sum` already gives 0.

## Code

```python
words = input().split()
total = sum(int(w) for w in words)
smallest = min((int(w) for w in words), default=None)
largest = max((int(w) for w in words), default=None)
print(f"Count: {len(words)}")
print(f"Sum: {total}")
print(f"Min: {'none' if smallest is None else smallest}")
print(f"Max: {'none' if largest is None else largest}")
if smallest is not None:
    print(f"Spread: {largest - smallest}")
```

## Why `is None` and not `if not smallest`

The smallest number could be `0`, which is falsy. `if not smallest` would treat it as "no
data". `is None` asks exactly the right question.

## Why the extra brackets

`min(int(w) for w in words, default=None)` is a `SyntaxError`: a bare generator expression
is only allowed as the **only** argument.
