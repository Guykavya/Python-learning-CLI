## Approach

Random pivot gives expected depth `O(log n)` for any input. The three-way split removes all copies of the pivot in one step, so many duplicates make the problem **easier**, not harder.

## Code

```python
import random

n = int(input())
a = [int(x) for x in input().split()]


def quick(a):
    if len(a) <= 1:
        return a
    pivot = a[random.randrange(len(a))]
    less = [x for x in a if x < pivot]
    equal = [x for x in a if x == pivot]
    greater = [x for x in a if x > pivot]
    return quick(less) + equal + quick(greater)


print(" ".join(map(str, quick(a))))
```

## Complexity

Expected O(n log n) time (O(n) with few distinct values), O(n) extra memory in this list-building form, expected recursion depth O(log n).

## Another way

The in-place Dutch-flag version keeps three pointers `lt`, `i`, `gt` over the array (like problem p017) and recurses on `a[lo:lt]` and `a[gt+1:hi]`; to be safe, recurse into the smaller part and loop on the larger one so the stack stays `O(log n)`. Median of three is a deterministic alternative to a random pivot, but adversarial inputs exist.
