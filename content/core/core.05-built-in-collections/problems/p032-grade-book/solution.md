## Approach

Group first (dict of lists), then summarise each group, then sort tuples that start with the
negative average.

## Code

```python
marks = {}
while True:
    line = input()
    if line == "end":
        break
    name, mark = line.split()
    marks.setdefault(name, []).append(int(mark))
rows = sorted((-sum(ms) / len(ms), name, len(ms)) for name, ms in marks.items())
if not rows:
    print("No marks.")
for neg, name, count in rows:
    print(f"{name}: {-neg:.1f} ({count} marks)")
```

## Complexity

O(n) to group n marks and O(k log k) to sort k students.
