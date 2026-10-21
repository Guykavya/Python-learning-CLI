# The harmonic total, fast

In "The loop with a growing step" you traced this program and found that `count` equals
`n // 1 + n // 2 + ... + n // n`:

```python
count = 0
for i in range(1, n + 1):
    for j in range(i, n + 1, i):
        count += 1
print(count)
```

`starter.py` runs exactly that. Make it fast enough for `n = 10^12`.

A single loop computing `n // i` for every `i` is O(n): fine for `n = 10^7`, but 10^12 steps would take days.
You need about O(sqrt(n)).

## Input

One line with an integer `n`.

## Output

One line with one integer: `n // 1 + n // 2 + ... + n // n`.

## Examples

| Input | Output |
|---|---|
| `1` | `1` |
| `6` | `14` |
| `12` | `35` |
| `30` | `111` |

## Constraints

- `1 <= n <= 10^12`

Use `input()` without a prompt message.

## Before you code

The answer counts pairs `(i, m)` of positive whole numbers with `i * m <= n` (take `m` = the multiple number).
Draw those pairs as dots on a grid for `n = 12`. The picture is symmetric about the diagonal `i = m`. How can you
count only one side?
