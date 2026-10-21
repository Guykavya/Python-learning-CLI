# How much extra memory?

Time is not the only cost. For each snippet, state the **extra space** it uses (not counting the input list `a`
of length `n` itself) in Big-O, and its time complexity. Justify each in a sentence or two.

**A**
```python
total = 0
for x in a:
    total += x
```

**B**
```python
squares = [x * x for x in a]
```

**C**
```python
rest = a
while len(rest) > 0:
    print(rest[0])
    rest = rest[1:]
```

**D**
```python
table = [[0] * n for _ in range(n)]
```

**E**
```python
seen = set()
for x in a:
    seen.add(x % 10)
```

**F** (a recursive function; read `def` as "a named piece of code that can call itself")
```python
def total(a, i):
    if i == len(a):
        return 0
    return a[i] + total(a, i + 1)

print(total(a, 0))
```

In `answer.md`, give your answers, then explain in a short paragraph why snippet F crashes with
`RecursionError` for `n = 5000`, even though snippet A works for `n = 10^7`.
