## Hint 1

How do you get `n` values that are each 0 or 1 from a Generator (Ch. 13.1; the upper bound is excluded)? Which function turns them into the number of heads so far (Ch. 10.5)?

## Hint 2

The running total after flip `i` (0-based) counts `i + 1` flips. Which array holds `1, 2, …, n`, so that one division gives every running mean?

## Hint 3

```text
flips = rng.integers(0, 2, size=n)
return cumsum(flips) / arange(1, n + 1)
```
