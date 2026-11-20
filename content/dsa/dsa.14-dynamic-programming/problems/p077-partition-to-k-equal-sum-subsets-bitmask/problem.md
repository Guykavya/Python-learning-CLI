# Partition to k equal sum subsets (bitmask)

Four friends share the cost of a trip by splitting a pile of receipts so that everybody pays the same amount. In general: write `can_split(nums, k)` that returns `True` if the list `nums` can be divided into `k` groups with **equal sums**, every number in exactly one group, and `False` otherwise.

You met this problem with backtracking in dsa.07. Here, solve it with a **bitmask DP** over the set of numbers already placed (chapter section 19).

## Example

```python
>>> can_split([4, 3, 2, 3, 5, 2, 1], 4)     # (5), (1, 4), (2, 3), (2, 3)
True
>>> can_split([1, 2, 3, 4], 3)              # total 10 is not a multiple of 3
False
>>> can_split([2, 2, 2, 2, 3, 4, 5], 4)     # total 20, target 5 each, but no way to pair them
False
>>> can_split([7], 1)
True
```

## Constraints

- `1 <= len(nums) <= 16`, `1 <= k <= len(nums)`; numbers from 1 to 10**4.
- `O(2**n * n)` time. A backtracking search without good pruning can take minutes on the `False` cases of the tests.

## Think about

1. If the groups are filled **one after another**, and you know the set of numbers used so far, do you also need to know how full the current group is? (Hint: it can be computed from the set.)
2. So what is the smallest state, and what does `f[mask]` need to store: a `True` / `False`, or something more?
3. Which numbers are allowed to be added to the current group?
4. Which quick checks give `False` before any DP?
