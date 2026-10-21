## Approach

First simulate small cases by hand to see the shape of the answer. For `h = 10, u = 3, d = 1`:

| day | morning | after climb | escaped? | after night |
|---|---|---|---|---|
| 1 | 0 | 3 | no | 2 |
| 2 | 2 | 5 | no | 4 |
| 3 | 4 | 7 | no | 6 |
| 4 | 6 | 9 | no | 8 |
| 5 | 8 | 11 | yes (11 >= 10) | |

Observations:

1. If `u >= h`, it escapes on day 1. This must be checked first, even if `d` is huge.
2. Otherwise, if `u <= d`, each morning it is no higher than before, so it never escapes.
3. Otherwise each full day-and-night gains `gain = u - d`. On the morning of day `k` the snail is at
   `(k - 1) * gain`, and it escapes that day if `(k - 1) * gain + u >= h`, that is
   `(k - 1) * gain >= h - u`. The smallest such `k - 1` is the **ceiling** of `(h - u) / gain`.

Ceiling division with integers: for positive `a` and `b`, `ceil(a / b) == (a + b - 1) // b`.
Adding `b - 1` pushes any non-zero remainder over the next multiple, but leaves an exact multiple alone.

## Trace

Input `10`, `3`, `1`:

| variable | value |
|---|---|
| `u >= h`? | 3 >= 10, no |
| `u <= d`? | 3 <= 1, no |
| gain | 2 |
| need | 7 |
| full_days | (7 + 1) // 2 = 4 |
| output | 5 |

## Code

```python
h = int(input())
u = int(input())
d = int(input())

if u >= h:
    # It climbs out on the very first day; the night never comes.
    print(1)
elif u <= d:
    # It never gains height overall, and one climb is not enough.
    print("never")
else:
    gain = u - d          # net progress per full day and night
    need = h - u          # morning height needed so that one more climb is enough
    full_days = (need + gain - 1) // gain    # ceiling of need / gain, with integers only
    print(full_days + 1)
```

## Complexity

A fixed number of operations: O(1) time and memory, whatever the size of `h`.

## Another way

**Simulate, but in jumps.** Simulation is the honest way to check a formula, so write it first for
small inputs and compare it with the formula on many random cases (that is what the tests do).
Simulation alone is fine when the numbers are small (say `h <= 10^6`); it is also the only easy option
when the rules change from day to day (for example if the snail gets tired and climbs less each day),
where no simple formula exists.

## Edge cases

- `u == h`: reaching exactly `h` counts, so day 1.
- `u == d` with `u < h`: `never`.
- `h - u` an exact multiple of `gain` (`9 3 1`): ceiling equals floor, answer 4, not 5.
- `d = 0`: no slide; the formula still works with `gain = u`.
