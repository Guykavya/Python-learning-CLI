# Trace: count the pruned calls

`count_nodes` runs include/exclude subset-sum and returns `(found, nodes)`: how many subsets reach the target and how many calls were made. With `check=True` a branch whose remaining target is already negative stops at once.

Predict **exactly** what the program prints. Do not run it.

```python
def count_nodes(nums, target, check):
    nodes = 0
    found = 0

    def go(i, remaining):
        nonlocal nodes, found
        nodes += 1
        if remaining == 0:
            found += 1
            return
        if check and remaining < 0:
            return
        if i == len(nums):
            return
        go(i + 1, remaining - nums[i])
        go(i + 1, remaining)

    go(0, target)
    return found, nodes


print(count_nodes([3, 5, 8], 8, False))
print(count_nodes([3, 5, 8], 8, True))
print(count_nodes([5, 8, 3], 8, False))
print(count_nodes([5, 8, 3], 8, True))
```

Write your answer in `answer.txt`, one printed line per line. Each line is a tuple such as `(2, 13)`.

## How to work

Draw the include/exclude tree for `[3, 5, 8]`: level `i` decides about `nums[i]`, the left child includes it (`remaining - nums[i]`), the right child excludes it. Write `remaining` in each node. A node stops when `remaining == 0` (found), when `check` is on and `remaining < 0`, or when `i == 3`.
Then do the same for the order `[5, 8, 3]`.

## After you answer

1. For `[3, 5, 8]` the check saved nothing. Where in the tree did the negative remainders appear?
2. For `[5, 8, 3]`, which node did the check stop, and how many calls did that save?
3. What does this say about putting big numbers first (chapter section 9, "The order of the choices matters")?
