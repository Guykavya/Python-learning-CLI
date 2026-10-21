## Approach

Two counters, both starting at 0. Read the numbers one at a time; no need to store them. A number is even exactly when
`x % 2 == 0`. Everything else is odd, so use `else` rather than testing `x % 2 == 1` separately.

In Python, `x % 2` is always 0 or 1 for any integer, even negative ones (`-3 % 2` is `1`), so the check is safe.
In languages like C or Java, `-3 % 2` is `-1`, and a test like `x % 2 == 1` would miss negative odd numbers.
Writing `x % 2 == 0` with an `else` works in every language.

## Trace

Input `5`, then `1 2 3 4 0`.

| Iteration | `x` | `x % 2` | `even` after | `odd` after |
|---|---|---|---|---|
| 1 | 1 | 1 | 0 | 1 |
| 2 | 2 | 0 | 1 | 1 |
| 3 | 3 | 1 | 1 | 2 |
| 4 | 4 | 0 | 2 | 2 |
| 5 | 0 | 0 | 3 | 2 |

Output: `even 3` then `odd 2`.

## Code

```python
c = int(input())
even = 0
odd = 0
for _ in range(c):
    x = int(input())
    if x % 2 == 0:
        even += 1
    else:
        odd += 1
print("even", even)
print("odd", odd)
```

## Complexity

One pass over the `c` numbers: O(c) time. Only two counters are kept, so O(1) extra memory.

## Another way

Count only the even numbers, then compute the odd count as `c - even`. That saves one counter and one branch.
Use it when there are exactly two categories that cover everything; use separate counters when there are
more categories or some numbers fit none of them.

## Edge cases

- `c = 0`: the loop never runs; print `even 0` and `odd 0`.
- `0` is even.
- Negative odd numbers like `-7` must count as odd.
