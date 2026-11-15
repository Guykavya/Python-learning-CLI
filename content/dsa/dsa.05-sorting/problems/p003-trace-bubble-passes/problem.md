# Trace bubble sort passes

Predict **exactly** what this program prints. Do not run it.

```python
a = [5, 1, 4, 2, 8]
swaps = 0
for p in range(len(a) - 1):
    for i in range(len(a) - 1 - p):
        if a[i] > a[i + 1]:
            a[i], a[i + 1] = a[i + 1], a[i]
            swaps += 1
    print("pass", p + 1, a, swaps)
print("sorted:", a)
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

Write the list after every single comparison on scratch paper. In pass `p` the inner loop looks at the pairs `(0,1)`, `(1,2)`, ... and
stops earlier each time (`len(a) - 1 - p` pairs), because the largest `p` values are already at the end.
Note that this version has **no early exit**: it prints a line for every pass, even when nothing moves.

## After you answer

1. After pass 1, which value is guaranteed to be at the end? Why?
2. In which pass did the last swap happen? How could the code stop earlier?
3. The final `swaps` equals the number of *inversions* of the start list. Count them: pairs `i < j` with `a[i] > a[j]`.
