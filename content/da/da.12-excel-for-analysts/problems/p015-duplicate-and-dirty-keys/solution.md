## Approach

Four different problems need four different views of the key: the normalised key for duplicates (Excel matches case-insensitively), the exact text for spaces, the group of spellings for case variants, and the type for numbers stored as text.

## Code

```python
from collections import Counter, defaultdict


def key_report(keys):
    norm_count = Counter()
    spellings = defaultdict(set)
    spaces, digits = set(), set()
    for k in keys:
        if k is None or str(k).strip() == "":
            continue
        n = str(k).strip().upper()
        norm_count[n] += 1
        if isinstance(k, str):
            spellings[n].add(k.strip())
            if k != k.strip():
                spaces.add(k)
            if k.strip().isdigit():
                digits.add(k)
    return {"duplicates": sorted(n for n, c in norm_count.items() if c > 1),
            "with_spaces": sorted(spaces),
            "case_variants": sorted(n for n, s in spellings.items() if len(s) > 1),
            "numbers_as_text": sorted(digits)}
```

## Complexity

O(n log n).

## Another way

In Excel: `=COUNTIF($A$2:$A$31, A2)` next to the key column (greater than 1 means a duplicate) and `=LEN(A2)<>LEN(TRIM(A2))` for stray spaces; in pandas, `s.duplicated()` and `s.str.strip()`.
