## Approach

Walk down from the root with a running sum. A downward path that ends at the current node and adds up to `target` is the stretch between an earlier point on the same root path and this node, so the earlier point must have had the running sum `running - target`. A dictionary `counts` says how often each running sum occurred on the **current** root path; `counts = {0: 1}` stands for the empty start before the root. At each node: add its value, count `counts[running - target]`, record the new running sum, visit both children, and remove the running sum again, because the sibling branch is a different root path.

## Code

```python
def path_sum_count(root, target):
    counts = {0: 1}                                     # the empty stretch before the root
    total = 0

    def go(node, running):
        nonlocal total
        if node is None:
            return
        running += node.val
        total += counts.get(running - target, 0)        # paths that end at this node
        counts[running] = counts.get(running, 0) + 1    # choose
        go(node.left, running)
        go(node.right, running)
        counts[running] -= 1                            # un-choose

    go(root, 0)
    return total
```

## Complexity

`O(n)` time: each node is entered once and does a constant number of dictionary operations. `O(h)` extra memory for the recursion and for the dictionary, which holds at most one entry per node of the current root path.

## Another way

Start a downward walk at every node and count the ends that give the target: simple, but `O(n * h)` (`O(n^2)` on a chain), and it is exactly what the pointer counter rejects. The prefix-sum idea is the same as the subarray-sum-equals-k problem of dsa.03 and dsa.04, with the array replaced by "the current root path" and the extra backtracking step.
