# Aliases, shallow and deep copies

Predict **exactly** what this program prints, one line per printed line. Do not run it.
Draw names, lists and arrows on paper as you go.

```python
import copy
a = [1, [2, 3], 4]
b = a
c = a[:]
d = copy.deepcopy(a)
b[0] = 100
c[1].append(5)
c[2] = 400
d[1].append(6)
print(a)
print(b)
print(c)
print(d)
print(a is b, a is c, a[1] is c[1], a[1] is d[1])
e = list(a)
a[1] = [9]
print(e[1], a[1])
a += [7]
print(len(b), len(c))
a = a + [8]
print(len(a), len(b))
```

Write your answer in `answer.txt`.
