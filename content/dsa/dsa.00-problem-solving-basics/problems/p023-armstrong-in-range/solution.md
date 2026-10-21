## Approach

Loop over every `x` from `lo` to `hi` inclusive. For each one, do two passes over its digits:

1. Count the digits `k`. Starting `k` at 1 and then dividing `x // 10` repeatedly makes 0 count as one digit.
2. Add up `(digit) ** k` for each digit, using `% 10` to read the last digit and `// 10` to drop it.

If the sum equals `x`, print it and set `found = True`. After the loop, print `none` if nothing was found.

`0` works out: the second loop never runs, so `total` is 0, which equals `x`.

## Trace

For `x = 371` (the outer loop is at this value):

| pass | t | t % 10 | k | total after |
|---|---|---|---|---|
| count | 37 | | 2 | |
| count | 3 | | 3 | |
| count | 0 | | 3 (stop) | |
| sum | 371 | 1 | 3 | 1 |
| sum | 37 | 7 | 3 | 1 + 343 = 344 |
| sum | 3 | 3 | 3 | 344 + 27 = 371 |

`total == 371`, so `371` is printed.

## Code

```python
lo = int(input())
hi = int(input())

found = False
for x in range(lo, hi + 1):
    # count the digits (0 counts as one digit)
    k = 1
    t = x // 10
    while t > 0:
        k += 1
        t //= 10

    # add up each digit to the power k
    total = 0
    t = x
    while t > 0:
        total += (t % 10) ** k
        t //= 10

    if total == x:
        print(x)
        found = True

if not found:
    print("none")
```

## Complexity

Each number takes about 2d steps, where d is its number of digits (at most 6 here).
So the total is O((hi - lo) x d), roughly a million simple steps for the widest range.

## Another way

**Track the digit count instead of recounting.** As `x` increases, the digit count only changes at 10, 100,
1000, ... So keep `k` and a variable `next_power = 10 ** k`; when `x` reaches `next_power`, increase `k` and
multiply `next_power` by 10. This removes the counting loop. It is a little faster but easier to get wrong;
recounting is simpler and fast enough here. For much bigger ranges you would instead **generate** digit
combinations rather than test every number, because Armstrong numbers are very rare.

## Edge cases

- `lo = hi`: one number to check; print it or `none`.
- The range `0` to `9`: all ten numbers are printed.
- A range with no Armstrong numbers, such as `10` to `100`: print `none` exactly once.
