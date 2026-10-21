## Approach

A whole number is even when dividing by 2 leaves remainder 0. The starter checked for remainder 1,
which is the test for "odd", so every answer was upside down. Python's `%` always gives a result
with the sign of the right-hand number, so `-3 % 2` is `1` and `-4 % 2` is `0`: negatives work
without a special case.

## Code

```python
def is_even(n):
    return n % 2 == 0
```

## Complexity

O(1).

## Another way

`n & 1 == 0` also works for whole numbers (the lowest bit of an even number is 0), but `% 2` says
what you mean.
