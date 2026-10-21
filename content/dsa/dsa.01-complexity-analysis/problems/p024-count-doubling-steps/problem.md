# Count the doubling steps by formula

`starter.py` reads `n` and runs this:

```python
count = 0
for i in range(1, n + 1):
    j = 1
    while j <= i:
        count += 1
        j = j * 2
print(count)
```

For each `i`, the inner loop doubles `j` from 1 until it passes `i`. The program prints how many times
`count += 1` runs in total. It is correct, but it takes O(n log n) time, which is hopeless for `n = 10^18`.

Make it fast: compute the same number in O(log n) steps or fewer.

## Input

One line with an integer `n`.

## Output

One line with one integer.

## Examples

| Input | Output | Why |
|---|---|---|
| `1` | `1` | i = 1: j = 1 (1 step) |
| `4` | `8` | i = 1: 1 step; i = 2: 2; i = 3: 2; i = 4: 3 |
| `7` | `17` | the steps for i = 1..7 are 1, 2, 2, 3, 3, 3, 3 |

## Constraints

- `1 <= n <= 10^18`

Use `input()` without a prompt message. Do not use floating-point logarithms (`math.log`): for large `n` they can be
off by one.

## Before you code

Make a table of `i` and the number of steps for `i = 1` to `16`. Which values of `i` share the same number of steps,
and how many of them are there?
