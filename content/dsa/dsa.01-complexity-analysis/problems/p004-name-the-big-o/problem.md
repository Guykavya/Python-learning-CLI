# Name the Big-O

For each snippet, state its time complexity in Big-O notation **in terms of the given sizes**, and justify it in
one or two sentences: which line runs most often, and how many times?

`a` and `b` are lists with `n` and `m` elements. All values are integers.

**A**
```python
total = 0
for x in a:
    total += x
print(total)
```

**B**
```python
count = 0
for i in range(n):
    for j in range(i + 1, n):
        if a[i] == a[j]:
            count += 1
```

**C**
```python
steps = 0
while n > 1:
    n = n // 2
    steps += 1
```

**D**
```python
for i in range(n):
    k = 1
    while k < n:
        k = k * 2
```

**E**
```python
for i in range(100):
    for x in a:
        print(i, x)
```

**F**
```python
for x in a:
    print(x)
for y in b:
    print(y)
```

**G**
```python
common = 0
for x in a:
    if x in b:
        common += 1
```

Write your answers in `answer.md`. Snippet G has a hidden loop. Find it.
