## Approach

Normalise once (not inside the loop), then compare each unordered pair exactly once with two nested loops where `j`
starts after `i`: that already excludes the name with itself and the mirrored pair, and it produces the pairs in sorted
order. `ratio() >= threshold` makes the limit part of the result. Returning *positions* rather than names keeps repeated
names apart and lets the caller look at the original rows. For 300 names there are 44,850 pairs, about a second of work
with a plain loop.

## Code

```python
from difflib import SequenceMatcher


def _normalise(name):
    return " ".join(name.lower().split())


def similar_names(names, threshold=0.85):
    keys = [_normalise(n) for n in names]
    pairs = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            if SequenceMatcher(None, keys[i], keys[j]).ratio() >= threshold:
                pairs.append((i, j))
    return pairs
```

## Complexity

O(n^2) pairs, each comparison costs time roughly quadratic in the name length (short names: fast). That is why the
chapter says: **block first**. Only compare names that already agree on something cheap (same city, same birth year);
a million rows are out of reach for all pairs.

## Another way

The reference solution of this course reuses one `SequenceMatcher` (`set_seq2` once per `j`, `set_seq1` for each `i`)
and calls `real_quick_ratio()` and `quick_ratio()` first: both are cheap upper bounds of `ratio()` (the documentation
says so), so a pair that fails them cannot pass `ratio()`. The answer is identical and about six times faster on 300
names. Do the simple version first, measure, then optimise.
