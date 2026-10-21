## Approach

A value that means "stop" instead of "data" is called a **sentinel**. The standard pattern is:
read one value before the loop, loop while it is not the sentinel, and read the next value as the last
step of the loop body. Then the sentinel is checked before it can ever be used as data.

The average only needs the running `total` and `count`, not the numbers themselves. The format spec `:.2f`
prints exactly two decimals. If the first value is `0`, the loop body never runs and only `count 0` is printed;
there is never a division by zero, because we only divide inside the loop, where `count >= 1`.

## Trace

Input `4`, `1`, `7`, `0`:

| x | total after | count after | printed |
|---|---|---|---|
| 4 | 4 | 1 | `4.00` |
| 1 | 5 | 2 | `2.50` |
| 7 | 12 | 3 | `4.00` |
| 0 | (loop ends) | 3 | `count 3` |

## Code

```python
total = 0
count = 0

x = int(input())
while x != 0:
    total += x
    count += 1
    print(f"{total / count:.2f}")
    x = int(input())

print("count", count)
```

## Complexity

One loop round per data number: O(n) time. Only two numbers are stored: O(1) space, no matter how long the input is.

## Another way

**`while True` with `break`.** Write `while True:`, read `x` at the top, and `if x == 0: break` right after.
Then there is only one `input()` line instead of two. Both are standard; the `break` version is handy when the
reading step is long, and the "read before, read at the end" version makes the stop condition visible in the
`while` line itself.

## Edge cases

- First value `0`: no averages, only `count 0`, and no division by zero.
- Averages between -1 and 0 print with the minus sign, like `-0.50`.
- Big totals: Python integers do not overflow, and the division happens only when printing.
