# Count the pairs without looping

`starter.py` reads `n` and prints how many times the inner line of this double loop runs:

```python
count = 0
for i in range(n):
    for j in range(i + 1, n):
        count += 1
print(count)
```

It is correct, but it really runs the loops. For `n = 100000` that is about five billion steps, which takes
many minutes in Python, and for `n = 10^18` it would never finish.

Make it fast: print the same number **without** running the loops, using a formula.

## Input

One line with an integer `n`.

## Output

One line with one integer: the number of times `count += 1` runs.

## Examples

| Input | Output | Why |
|---|---|---|
| `4` | `6` | i = 0: j = 1, 2, 3; i = 1: j = 2, 3; i = 2: j = 3; i = 3: none. 3 + 2 + 1 + 0 |
| `1` | `0` | the inner range is empty |
| `0` | `0` | the outer range is empty |

## Constraints

- `0 <= n <= 10^18`

Use `input()` without a prompt message. Your program must finish in well under a second.

## Before you code

Run the starter for `n = 1, 2, 3, 4, 5, 6` and write the answers in a table. What is the pattern?
