## Approach

Each rule is one `if`. A missing field is reported once; the later rules only run on the fields that exist, so one missing field does not cause a cascade of messages.

## Code

```python
REQUIRED = ["name", "numerator", "grain", "owner", "direction", "type", "unit"]
TYPES = {"leading", "lagging", "guardrail", "vanity"}


def check_kpi(defn):
    issues = [f"missing field: {f}" for f in REQUIRED if not defn.get(f)]
    t = defn.get("type")
    if t and t not in TYPES:
        issues.append(f"unknown type: {t}")
    if t == "vanity":
        issues.append("vanity metric: no decision depends on it")
    d = defn.get("direction")
    if d and d not in ("up", "down"):
        issues.append("direction must be 'up' or 'down'")
    if defn.get("unit") == "%" and not defn.get("denominator"):
        issues.append("a percentage needs a denominator")
    return issues
```

## Complexity

O(number of fields).

## Another way

A `dataclass` with typed fields and a `__post_init__` check refuses a bad definition when it is created, instead of listing problems later.
