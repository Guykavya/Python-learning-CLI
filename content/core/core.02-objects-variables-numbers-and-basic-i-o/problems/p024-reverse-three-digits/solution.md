## Approach

Split the number into its three place values, then put them back together in reverse order.

## Code

```python
n = int(input())
hundreds = n // 100
tens = n // 10 % 10
ones = n % 10
rev = ones * 100 + tens * 10 + hundreds
print(rev)
print(abs(n - rev))
```

## Why it handles 120 correctly

The reversed value is `0 * 100 + 2 * 10 + 1 = 21`. Because it is a number, there is no leading zero.

## A neat fact

The difference is always a multiple of 99: `|100a + 10b + c - (100c + 10b + a)| = 99 * |a - c|`.
