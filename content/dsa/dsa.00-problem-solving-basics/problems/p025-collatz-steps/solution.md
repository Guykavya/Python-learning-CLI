## Approach

This is a direct **simulation**: do exactly what the rule says, and keep two extra variables while you go.

- `steps` counts how many times the rule was applied. It starts at 0, so `n = 1` gives 0.
- `peak` is a running maximum. It starts at `n`, because the starting number counts.

Use `n //= 2` for halving. `//` keeps `n` an exact integer. With `n / 2` Python produces a float, which prints
as `16.0`, and once values pass about 9 x 10^15 a float can no longer store every whole number exactly, so
the sequence goes wrong and gives the wrong step count.

## Trace

Input `6`:

| step | n before | even? | n after | peak after |
|---|---|---|---|---|
| 1 | 6 | yes | 3 | 6 |
| 2 | 3 | no | 10 | 10 |
| 3 | 10 | yes | 5 | 10 |
| 4 | 5 | no | 16 | 16 |
| 5 | 16 | yes | 8 | 16 |
| 6 | 8 | yes | 4 | 16 |
| 7 | 4 | yes | 2 | 16 |
| 8 | 2 | yes | 1 | 16 |

Printed: `steps 8` and `peak 16`.

## Code

```python
n = int(input())

steps = 0
peak = n
while n != 1:
    if n % 2 == 0:
        n //= 2
    else:
        n = 3 * n + 1
    steps += 1
    if n > peak:
        peak = n

print("steps", steps)
print("peak", peak)
```

## Complexity

One loop round per step, so O(S) time where S is the step count, and O(1) space. Nobody knows a formula
for S, but for every `n` up to 10 to the power 12 it is below about 1500, so this is instant.

## Another way

**Combine the odd step with the halving.** When `n` is odd, `3n + 1` is always even, so the next step is
certainly a halving. You can do `n = (3 * n + 1) // 2` and add 2 to `steps` at once. This skips about a third
of the loop rounds. It is a nice trick when you must run Collatz for millions of starting values, but it
makes the peak harder to track (the value `3n + 1` itself must still be compared), so the plain version is
clearer here.

## Edge cases

- `n = 1`: the loop never runs; `steps 0`, `peak 1`.
- Powers of two such as 8: only halvings, and the peak is the start.
- Starts like 319804831, where the values climb above 10^18 before coming down.
