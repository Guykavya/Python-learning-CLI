## Approach

Carry the number spelled by the path so far down as a parameter. At each node it becomes `so_far * 10 + node.val`. A path is complete at a leaf, so a leaf returns the number. An inner node returns the sum of its two subtrees' answers. An empty child returns `0`, so a node with one child adds the single real path once.

## Code

```python
def sum_numbers(root):
    def go(node, so_far):
        if node is None:
            return 0
        so_far = so_far * 10 + node.val
        if node.left is None and node.right is None:      # a leaf: the number is complete
            return so_far
        return go(node.left, so_far) + go(node.right, so_far)

    return go(root, 0)
```

## Complexity

`O(n)` time, `O(h)` stack.

## Another way

Spell each path as a string and convert it with `int(...)` at the leaf (that is the test's brute force); or collect the paths with the backtracking of the previous problem and sum the converted strings. The version with a number is better because nothing is built or copied.
