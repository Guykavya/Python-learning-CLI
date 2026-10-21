## Approach

This is the reverse-number problem plus one comparison. A number is a palindrome exactly when it equals its own
reverse. Build the reverse with `rev = rev * 10 + n % 10` and `n //= 10`.

Two details:

- The loop shrinks `n` to 0, so keep the original value in another variable for the final comparison.
- Negatives are "no" straight away. (If you took `abs()` instead, `-121` would wrongly say `yes`.)

Trailing zeros take care of themselves: `10` reverses to `1`, and `1 != 10`, so the answer is `no`.
`0` reverses to `0`, so it is `yes`.

## Trace

Input `1221`, so `original = 1221`.

| Iteration | `n` before | `n % 10` | `rev` after | `n` after |
|---|---|---|---|---|
| 1 | 1221 | 1 | 1 | 122 |
| 2 | 122 | 2 | 12 | 12 |
| 3 | 12 | 2 | 122 | 1 |
| 4 | 1 | 1 | 1221 | 0 |

`rev == original` (1221 == 1221), so the output is `yes`.

## Code

```python
n = int(input())
if n < 0:
    print("no")
else:
    original = n
    rev = 0
    while n > 0:
        rev = rev * 10 + n % 10
        n //= 10
    if rev == original:
        print("yes")
    else:
        print("no")
```

## Complexity

One loop step per digit: O(d), where d is the number of digits.

## Another way

Reverse only half the number. Keep moving digits from `n` to `rev` while `n > rev`. When they meet, the number is
a palindrome if `n == rev` (even number of digits) or `n == rev // 10` (odd number of digits, the middle digit
is in `rev`). Numbers ending in 0 (other than 0 itself) must be rejected first, because `rev` would never get that
leading 0. This does half the work and never builds a number bigger than the input, which matters in languages
like C or Java where reversing a large number can overflow. In Python the full reverse is simpler and fine.

## Edge cases

- `0` and single digits: `yes`.
- Negative: always `no`.
- Ends in 0 (like `10` or `100`): the reverse loses the zeros, so it never equals the original. Correctly `no`.
- Zeros in the middle (like `1000021`): the full reverse `1200001` is compared digit for digit, so `no`.
