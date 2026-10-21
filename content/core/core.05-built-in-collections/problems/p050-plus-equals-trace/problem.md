# + versus +=

Predict **exactly** what this program prints, one line per printed line. Do not run it.
Draw names, lists and arrows on paper as you go.

```python
a = [1, 2]
b = a
a += [3]
print(a, b)
a = a + [4]
print(a, b)
t = (1, 2)
u = t
t += (3,)
print(t, u)
s = "hi"
r = s
s += "!"
print(s, r)
x = [[0]]
y = x * 2
y[0].append(1)
print(x, y)
y[1] = 5
print(x, y)
n = [1]
m = [n, n]
n += [2]
print(m)
n = n + [3]
print(m, n)
```

Write your answer in `answer.txt`.
