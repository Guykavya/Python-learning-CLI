# Best, average and worst case

The same code can be fast on one input and slow on another of the same size. For each snippet, describe an input
that gives the **best case** and one that gives the **worst case**, state both complexities, and say what the
**average case** is (and what "average" assumes).

**A. Linear search**
```python
pos = -1
for i in range(n):
    if a[i] == target:
        pos = i
        break
```

**B. Is the list sorted?**
```python
ok = True
for i in range(n - 1):
    if a[i] > a[i + 1]:
        ok = False
        break
```

**C. Insertion sort** (move each element left until it is in place)
```python
for i in range(1, n):
    j = i
    while j > 0 and a[j - 1] > a[j]:
        a[j - 1], a[j] = a[j], a[j - 1]
        j -= 1
```

**D. Dict lookup**: `d[key]` on a dict with `n` keys.

Then answer in a short paragraph: when a problem says "n <= 2 * 10^5" and you analyse your solution, which case do
you use, and why? Why is "it was fast on the examples" not evidence?
