## Approach

Keep a running `result` that starts at 1, the "empty product". Multiply it by `a` exactly `b` times.
Starting at 1 means `b = 0` is handled automatically: the loop does not run and the answer is 1.
Python integers grow as large as needed, so even `2` to the power `200` is exact.

## Trace

Input `-3` then `3`:

| round | result before | result after |
|---|---|---|
| 1 | 1 | -3 |
| 2 | -3 | 9 |
| 3 | 9 | -27 |

Printed: `-27`.

## Code

```python
a = int(input())
b = int(input())

result = 1
for _ in range(b):
    result *= a

print(result)
```

## Complexity

The loop runs `b` times, so the time is O(b) multiplications. Only one variable is stored: O(1) extra space
(ignoring that the number itself gets longer).

## Another way

**Fast power (repeated squaring).** Notice that `a` to the power 10 is (`a` to the power 5) squared.
Keep a `base` and look at `b` in binary: while `b > 0`, if `b % 2 == 1` multiply `result` by `base`;
then set `base = base * base` and `b = b // 2`. This needs only about log2(b) rounds instead of `b`.
For `b` up to 500 the simple loop is perfectly fast, but when the exponent is huge (say `10**18`, usually
combined with `%` to keep numbers small) repeated squaring is the only practical way.

## Edge cases

- `b = 0`: the loop never runs, result stays 1, also for `a = 0`.
- `a = 0`, `b > 0`: the result becomes 0 after the first round and stays 0.
- Negative `a`: the sign flips each round, so it ends negative only when `b` is odd.
