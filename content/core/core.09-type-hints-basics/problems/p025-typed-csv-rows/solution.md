## Approach

`parse_rows` is the boundary: the lines are untrusted text, so each check is explicit and runtime. Its return type is a fixed pair, `tuple[list[tuple[str, int]], list[str]]`: first the good rows, then the bad lines. Both lists are created with type hints, because they start empty.

`oldest` and `mean_age` can have no answer, so they return `X | None`. `age_buckets` creates the dict with all four keys up front, so callers can rely on every key existing.

## Code

```python
def parse_rows(lines: list[str]) -> tuple[list[tuple[str, int]], list[str]]:
    rows: list[tuple[str, int]] = []
    bad: list[str] = []
    for line in lines:
        if line.strip() == "":
            continue
        parts = line.split(",")
        if len(parts) != 2:
            bad.append(line)
            continue
        name = parts[0].strip()
        try:
            age = int(parts[1])
        except ValueError:
            bad.append(line)
            continue
        if name == "" or age < 0 or age > 150:
            bad.append(line)
            continue
        rows.append((name, age))
    return rows, bad


def oldest(rows: list[tuple[str, int]]) -> tuple[str, int] | None:
    best: tuple[str, int] | None = None
    for row in rows:
        if best is None or row[1] > best[1]:
            best = row
    return best


def age_buckets(rows: list[tuple[str, int]]) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = {"child": [], "teen": [], "adult": [], "senior": []}
    for name, age in rows:
        if age < 13:
            buckets["child"].append(name)
        elif age < 20:
            buckets["teen"].append(name)
        elif age < 65:
            buckets["adult"].append(name)
        else:
            buckets["senior"].append(name)
    return buckets


def mean_age(rows: list[tuple[str, int]]) -> float | None:
    if not rows:
        return None
    return sum(age for name, age in rows) / len(rows)
```

## Complexity

All four are O(n) in the number of lines or rows.

## Another way

`oldest` can be written `max(rows, key=lambda row: row[1])` after an emptiness check; `max` returns the first of equal items, so the tie rule still holds.
