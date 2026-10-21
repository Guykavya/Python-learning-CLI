# Tuple traps

Predict **exactly** what this program prints, one line per printed line. Do not run it.

```python
x = (7)
y = 7,
print(type(x), type(y))
print(y, len(y))
z = ()
print(z + (1, 2))
p, *q, r = [1, 2, 3, 4]
print(p, q, r)
a, b = 1, 1
for _ in range(3):
    a, b = b, a + b
print(a, b)
t = (1, [2])
t[1].append(99)
print(t)
print(len(t[1]))
```

Write your answer in `answer.txt`.
