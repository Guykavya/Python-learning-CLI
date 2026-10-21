# The shared-row trap

Predict **exactly** what this program prints, one line per printed line. Do not run it.
Draw names, lists and arrows on paper as you go.

```python
g = [[0] * 3] * 2
g[0][1] = 5
print(g)
h = [[0] * 3 for _ in range(2)]
h[0][1] = 5
print(h)
row = [0, 0]
m = [row, row]
m[1][0] = 7
print(m, row)
m[0] = [1, 1]
m[1][1] = 9
print(m)
k = [[]] * 3
k[0].append("x")
k[1] = k[1] + ["y"]
print(k)
print(k[0] is k[2], k[1] is k[0])
```

Write your answer in `answer.txt`.
