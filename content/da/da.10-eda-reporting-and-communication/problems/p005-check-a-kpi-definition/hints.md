## Hint 1

`defn.get(field)` returns `None` for a missing key. Which values count as "empty"? (`None` and `""`.) Keep the checks in the order of the statement so the list comes out in that order.

## Hint 2

```text
issues = []
for f in REQUIRED: if not defn.get(f): issues.append(f"missing field: {f}")
t = defn.get("type"); if t and t not in TYPES: ...; if t == "vanity": ...
d = defn.get("direction"); if d and d not in ("up", "down"): ...
if defn.get("unit") == "%" and not defn.get("denominator"): ...
```
