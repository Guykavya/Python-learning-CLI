## Approach

Every pattern problem starts the same way: find the rule that links the row number to what is printed on that row.
Here row `i` has `i` stars. Loop `i` from 1 to `n` and print `"*" * i`. For `n = 0` the range is empty and
nothing is printed.

## Trace

Input `4`.

| Iteration | `i` | `"*" * i` |
|---|---|---|
| 1 | 1 | `*` |
| 2 | 2 | `**` |
| 3 | 3 | `***` |
| 4 | 4 | `****` |

## Code

```python
n = int(input())
for i in range(1, n + 1):
    print("*" * i)
```

## Complexity

The program prints 1 + 2 + ... + n stars in total, which is `n * (n + 1) / 2`: O(n^2) characters.

## Another way

Use a nested loop, printing one star at a time with `end=""` and then ending the row with `print()`:

```python
n = int(input())
for i in range(1, n + 1):
    for j in range(i):
        print("*", end="")
    print()
```

This is longer, but it is the general tool: when a row has a mix of characters (spaces then stars, or numbers
that change along the row), string repetition alone is not enough and you need the inner loop.
