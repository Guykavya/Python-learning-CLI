# Trace: reading a defaultdict creates keys

`defaultdict` is convenient because `d[key]` never fails. The price: `d[key]` on a missing key
**stores** a new entry, even when you only meant to look. Some ways of reading do that, some do
not. Trace this program.

```python
from collections import defaultdict

stock = defaultdict(int)
stock["apple"] += 3
print(len(stock), dict(stock))

if stock["pear"] > 0:
    print("pears in stock")
print(len(stock), dict(stock))

print("plum" in stock, stock.get("plum"), len(stock))

groups = defaultdict(list)
for word in ["ant", "bee", "ape"]:
    groups[word[0]].append(word)
print(groups["c"], len(groups))
print(groups)

counts = defaultdict(int, {"x": 1})
total = 0
for key in ["x", "y", "z"]:
    total += counts[key]
print(total, list(counts))

plain = dict(counts)
print(plain.get("w", "missing"), "w" in counts)

counts.default_factory = None
try:
    counts["w"]
except KeyError as e:
    print("KeyError", e)

seen = defaultdict(int, {"a": 1, "b": 2})
try:
    for k in seen:
        seen[k + "!"]
except RuntimeError as e:
    print("RuntimeError:", e)
print(list(seen))
```

Write exactly what it prints, one line per output line, in `answer.txt`.

**Facts you need**

- A defaultdict prints like `defaultdict(<class 'list'>, {'a': [1]})`.
- `str()` of a `KeyError` is the missing key's repr, for example `'w'` (with quotes).
- If a dict changes size while a `for` loop is iterating over it, the **next** step of the loop
  raises `RuntimeError: dictionary changed size during iteration`.

**Example** (a different program)

```python
d = defaultdict(str)
print(len(d), d["k"] == "", len(d))     # 0 True 1
```
