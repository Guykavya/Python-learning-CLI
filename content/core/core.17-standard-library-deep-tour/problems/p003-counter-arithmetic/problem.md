# Trace: Counter arithmetic

A `Counter` is a multiset: you can add, subtract, intersect and unite two of them. The
operators and the methods do **not** treat zero and negative counts the same way, and that is
what this trace is about.

```python
from collections import Counter

a = Counter("banana")
b = Counter({"a": 1, "n": 5, "x": 2})
print(a)
print(a + b)
print(a - b)
print(b - a)
print(a & b)
print(a | b)
c = Counter(a)
c.subtract(b)
print(c)
print(+c)
print(c["zzz"], "zzz" in c)
c.update(["a", "q"])
print(c.most_common(2))
print(a.total(), b.total())
print(sorted(a.elements()))
```

Write exactly what the program prints, one line per `print`, in `answer.txt`.

**Rules you need**

- A `Counter` prints like `Counter({'a': 3, 'n': 2})`: items sorted by count, **highest first**;
  items with equal counts appear in the order they were first inserted.
- Counters remember insertion order like dicts. `Counter("banana")` meets `b` first, then `a`,
  then `n`.

**Example** (a different program)

```python
print(Counter("aab") + Counter("bc"))   # Counter({'a': 2, 'b': 2, 'c': 1})
```
