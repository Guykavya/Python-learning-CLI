## Approach

`itertools.combinations(palette, 2)` yields exactly the pairs `i < j` in the order asked. The simulated separation, not the normal-vision distance, is the quantity that matters.

## Code

```python
from itertools import combinations


def safe_pairs(palette, min_sep):
    return [(a, b) for a, b in combinations(palette, 2) if separation(a, b) >= min_sep]
```

(The starter's `simulate` and `separation` stay as they are.)

## Complexity

O(k^2) for `k` colours.

## Another way

Greedy palette building: add a colour only when it is at least `min_sep` away from every colour already chosen, which gives a full palette instead of a list of pairs.
