## Walkthrough

Counts after building: `to` 3, `be` 3, `or` 1, `not` 1, `that` 1, `is` 1, `the` 1, `question` 1 (in this insertion
order; `to` and `be` tie, so `to` is first).

After `c["or"] += 5`: `or` is 6. After `update(["is", "is"])`: `is` is 3.

## Output

```
Counter({'to': 3, 'be': 3, 'or': 1, 'not': 1, 'that': 1, 'is': 1, 'the': 1, 'question': 1})
3 0
[('to', 3), ('be', 3)]
[('or', 6), ('to', 3), ('be', 3)]
8 17
3
False
```

## Key ideas

- A `Counter` returns 0 for a missing key and does **not** insert it when you only read it.
- `most_common` orders by count; ties keep insertion order.
- `len(c)` is the number of distinct keys; `sum(c.values())` is the number of items counted.
- `update` with an iterable adds 1 per element; it does not replace counts.
