# Chains and short-circuits

Predict **exactly** what this program prints, one line per `print`. Do not run it.
One hint: none of these lines raises an error.

```python
x = 5
print(1 < x < 10)
print(1 < x > 3)
print(10 > x < 3)
print(x == 5 == 5.0)
print(0 < x != 5)
print(3 < x < 4 or x)
print(x > 0 and x * 2)
print(0 and 1 / 0)
print(x or 1 / 0)
print((x := 7) > 5, x)
print(x - 7 or "zero")
```

Write your answer in `answer.txt`.
