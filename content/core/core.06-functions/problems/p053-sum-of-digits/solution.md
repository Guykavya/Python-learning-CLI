## Approach

`n % 10` is the last digit and `n // 10` is the number without it. A single digit is the base
case. Negatives are made positive once, at the top; because the recursive call then always gets a
non-negative number, the check costs nothing afterwards.

## Code

```python
def sum_digits(n):
    """Return the sum of the decimal digits of n (sign ignored), recursively."""
    if n < 0:
        return sum_digits(-n)
    if n < 10:
        return n
    return n % 10 + sum_digits(n // 10)
```

## Complexity

O(d) calls for a d-digit number.

## Another way

`sum(int(ch) for ch in str(abs(n)))` is the string way. The arithmetic version shows the recursive structure of a number: its last digit plus the rest.
