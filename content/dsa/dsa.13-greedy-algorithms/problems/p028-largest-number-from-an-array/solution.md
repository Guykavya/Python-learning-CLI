## Approach

Sort the numbers as strings with the pairwise rule "`a` before `b` if `a + b > b + a`" (chapter section 12). The exchange argument: if two **neighbours** in the answer are in the wrong order (`b + a > a + b` but `a` comes first), swapping them changes only that part of the string and makes it bigger. So in the best answer no neighbours are out of order, which is exactly the sorted order under this rule. The rule is a consistent (transitive) order, so `sort` can use it.

```python
from functools import cmp_to_key


def largest_number(nums):
    strs = [str(x) for x in nums]

    def compare(a, b):
        if a + b > b + a:
            return -1            # a comes first
        if a + b < b + a:
            return 1
        return 0

    strs.sort(key=cmp_to_key(compare))
    result = "".join(strs)
    return "0" if result[0] == "0" else result      # [0, 0] -> "0", not "00"
```

If the first character is `"0"`, the largest piece is `0`, so every piece is `0`, and the whole number is zero.

## Complexity

`O(n log n)` comparisons, each `O(L)` for numbers of up to `L` digits: `O(n L log n)`. Space `O(n L)`.

## Another way

The exchange argument says "no two neighbours may be out of order". **Insertion sort** (dsa.05) uses exactly that: it swaps a new element left past every neighbour that should come after it. With the pairwise rule it needs no `cmp_to_key`, and it shows the greedy idea plainly. It is `O(n^2)` comparisons, fine for small lists.

```python
def largest_number(nums):
    strs = [str(x) for x in nums]
    for i in range(1, len(strs)):
        j = i
        while j > 0 and strs[j] + strs[j - 1] > strs[j - 1] + strs[j]:
            strs[j], strs[j - 1] = strs[j - 1], strs[j]      # neighbours out of order: swap
            j -= 1
    result = "".join(strs)
    return "0" if result[0] == "0" else result
```
