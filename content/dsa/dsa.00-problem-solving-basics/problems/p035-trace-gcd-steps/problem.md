# Trace Euclid's algorithm

Euclid's algorithm finds the greatest common divisor (gcd) of two numbers: the largest number that divides both.
Each step replaces the pair `(a, b)` with `(b, a % b)` until `b` becomes 0.

Predict **exactly** what this program prints. Do not run it. Work it with a trace table on paper.

```python
a = 252
b = 105
while b != 0:
    print(a, b)
    a, b = b, a % b
print("gcd", a)

a = 17
b = 5
while b != 0:
    print(a, b)
    a, b = b, a % b
print("gcd", a)

a = 18
b = 48
while b != 0:
    print(a, b)
    a, b = b, a % b
print("gcd", a)
```

Write your answer in `answer.txt`, one line per printed line, exactly as Python would print it
(`print(a, b)` puts one space between the values).

Look carefully at the third loop, where `a` is smaller than `b` at the start. What does the first step do?
