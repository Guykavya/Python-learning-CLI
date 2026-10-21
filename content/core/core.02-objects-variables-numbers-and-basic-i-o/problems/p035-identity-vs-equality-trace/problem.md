# Identity versus equality

Predict **exactly** what this program prints, one line per printed line. Do not run it.

```python
x = 300
y = x
print(x is y)
y += 1
print(x, y)
print(x is y)
a = 2.5
b = a
print(a == b, a is b)
c = float("2.5")
print(a == c)
print(type(c) is float)
n = None
print(n is None, n == None)
print(1 == 1.0)
print(type(1) is type(1.0))
print(isinstance(True, int))
print(id(a) == id(b))
```

Write your answer in `answer.txt`.
