## Hint 1

What are the last digit of 4729 and 'the rest' of it, using `%` and `//`?

## Hint 2

A one-digit number is its own digit sum. That is the base case. Where should negatives be handled so the recursion never sees them?

## Hint 3

```
if n < 0: return sum_digits(-n)
if n < 10: return n
return n % 10 + sum_digits(n // 10)
```
