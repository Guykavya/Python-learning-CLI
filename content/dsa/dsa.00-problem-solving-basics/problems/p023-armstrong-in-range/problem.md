# Armstrong numbers in a range

A number is an **Armstrong number** if it equals the sum of its digits, each raised to the power of
how many digits the number has.

- `153` has 3 digits, and 1^3 + 5^3 + 3^3 = 1 + 125 + 27 = 153, so 153 is an Armstrong number.
- `154` has 3 digits, and 1^3 + 5^3 + 4^3 = 190, which is not 154, so it is not.
- `9474` has 4 digits, and 9^4 + 4^4 + 7^4 + 4^4 = 6561 + 256 + 2401 + 256 = 9474. Armstrong.
- Every single-digit number `0` to `9` is an Armstrong number, because d^1 = d. (Treat `0` as having one digit.)

Read two numbers `lo` and `hi` and print every Armstrong number `x` with `lo <= x <= hi`.

**Rule:** work with arithmetic only (`%` and `//`). Do not convert numbers to strings (no `str()`).

## Input

Two lines: `lo`, then `hi`. Use `input()` without a prompt message.

## Output

Every Armstrong number in the range, one per line, in increasing order.
If there is none, print exactly one line: `none`.

## Examples

Input `100` then `500`:

```
153
370
371
407
```

Input `8` then `12`:

```
8
9
```

Input `10` then `100`:

```
none
```

## Constraints

- `0 <= lo <= hi <= 100000`
- Both ends are included.
- Time limit: a few seconds.

## Before you code

Check by hand that 370 is an Armstrong number. Notice that you need to go over the digits **twice**:
once to count them, once to add up the powers. Write your plan as comments at the top of `solution.py`.
