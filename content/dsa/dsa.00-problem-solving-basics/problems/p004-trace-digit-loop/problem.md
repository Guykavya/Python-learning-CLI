# Trace a digit-peeling loop

Predict **exactly** what this program prints. Do not run it. Trace it on paper with a table:
one column per variable, one row per loop iteration.

```python
n = 5207
step = 0
while n > 0:
    step += 1
    digit = n % 10
    n = n // 10
    print("step", step, "digit", digit, "left", n)
print("done after", step, "steps")

m = 1000
zeros = 0
while m > 0:
    if m % 10 == 0:
        zeros += 1
    m //= 10
    print("m is now", m)
print("zeros:", zeros)
```

Write your answer in `answer.txt`, one line per printed line, exactly as Python would print it
(`print` with several values puts one space between them).
