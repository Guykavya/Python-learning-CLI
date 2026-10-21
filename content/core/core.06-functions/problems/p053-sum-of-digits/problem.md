# Sum of digits by recursion

Write `sum_digits(n)` **recursively** that returns the sum of the decimal digits of the integer
`n`. For a negative number, ignore the sign.

Use arithmetic (`% 10` and `// 10`), not `str(n)`.

**Examples**

```python
sum_digits(4729)    # 22
sum_digits(5)       # 5
sum_digits(0)       # 0
sum_digits(-305)    # 8
sum_digits(10**30)  # 1
```
