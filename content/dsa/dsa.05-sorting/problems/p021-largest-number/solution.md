## Approach

A comparator that looks at the two possible concatenations defines the best order. Sort with `cmp_to_key`, join, and fix the all-zero result.

## Code

```python
from functools import cmp_to_key

n = int(input())
a = input().split()


def cmp(x, y):
    if x + y > y + x:
        return -1
    if x + y < y + x:
        return 1
    return 0


a.sort(key=cmp_to_key(cmp))
result = "".join(a)
print("0" if result[0] == "0" else result)
```

## Complexity

O(n log n) comparisons, each comparing strings of length at most 20, so O(n log n) overall.

## Another way

A key function instead of a comparator: `key=lambda s: s * 10` sorted in reverse works because repeating a string at least as often as the maximum length makes plain string order match the concatenation order. The comparator version is the one that generalises.
