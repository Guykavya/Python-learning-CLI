## Approach

A separate `height` call at every node walks the same subtrees again and again. Instead let one recursive function do both jobs: it returns the height of the subtree, or `-1` meaning "this subtree is already unbalanced". Check the left side first; if it failed, stop. Then the right side. If the heights differ by more than 1, return `-1`. Otherwise return the height. The tree is balanced exactly when the root's answer is not `-1`.

## Code

```python
def is_balanced(root):
    def check(node):                                # the height of the subtree, or -1 if it is unbalanced
        if node is None:
            return 0
        left = check(node.left)
        if left == -1:
            return -1
        right = check(node.right)
        if right == -1 or abs(left - right) > 1:
            return -1
        return 1 + max(left, right)

    return check(root) != -1
```

## Complexity

`O(n)` time: every node is visited once. `O(h)` stack. The naive version (call `height` for both children at every node) costs `O(n log n)` on a balanced tree and `O(n^2)` on a chain.

## Another way

The slow version is a good brute force for testing: `abs(height(left) - height(right)) <= 1 and is_balanced(left) and is_balanced(right)` (the test file uses one). Another way to return two things: return a pair `(balanced, height)` from the recursion instead of the `-1` signal. It is clearer, and a little slower because of the tuples.
