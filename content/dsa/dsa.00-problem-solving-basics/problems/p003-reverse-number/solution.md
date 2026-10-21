## Approach

Peel digits off the right of `n` with `% 10` and `// 10`, and push each one onto the right of a new number `rev`
with `rev = rev * 10 + digit`. The first digit peeled (the last digit of `n`) ends up as the leftmost digit of `rev`.

Handle the sign separately: remember whether `n` was negative, work with `abs(n)`, and put the minus sign back at the end.
Zeros at the end of `n` (like in `1200`) become leading zeros of `rev`. They vanish on their own, because
`0 * 10 + 0` is still `0`.

## Trace

Input `1200`.

| Iteration | `n` before | `digit` | `rev` after | `n` after |
|---|---|---|---|---|
| 1 | 1200 | 0 | 0 | 120 |
| 2 | 120 | 0 | 0 | 12 |
| 3 | 12 | 2 | 2 | 1 |
| 4 | 1 | 1 | 21 | 0 |

Output: `21`.

## Code

```python
n = int(input())
negative = n < 0
n = abs(n)
rev = 0
while n > 0:
    digit = n % 10
    rev = rev * 10 + digit
    n //= 10
if negative:
    rev = -rev
print(rev)
```

## Complexity

One loop step per digit: O(d), where d is the number of digits (about log10 n).

## Another way

You could first count the digits (as in the previous problem), then place each peeled digit directly at its
final position by multiplying it by the right power of 10. That needs two passes and a power of 10,
so it is longer and easier to get wrong. The `rev * 10 + digit` trick is the one to remember: it is the
standard way to build a number digit by digit, and you will use it again (for palindromes, for parsing digits, and more).

## Edge cases

- `0`: the loop never runs and `rev` stays `0`. Correct.
- `-123`: the sign is stored first, so the answer is `-321`.
- Trailing zeros: `1200` gives `21`, not `0021`.
