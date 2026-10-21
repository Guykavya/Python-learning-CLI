## Approach

Parse each line into a dict, then merge with the pipe operator: `old | new`. When a key is in
both, the right-hand value wins, which is exactly "new price wins".

## Code

```python
old = {}
for pair in input().split():
    name, price = pair.split("=")
    old[name] = int(price)
new = {}
for pair in input().split():
    name, price = pair.split("=")
    new[name] = int(price)
merged = old | new
for item in sorted(merged):
    print(f"{item}: {merged[item]}")
changed = sorted(item for item in new if item in old and old[item] != new[item])
print("Changed:", ", ".join(changed) if changed else "none")
```

## Complexity

Parsing and merging are O(n + m). Sorting the keys is O(k log k) for k distinct items.

## Another way

`merged = dict(old)` then `merged.update(new)` does the same as `old | new` and works on older
Python versions.
