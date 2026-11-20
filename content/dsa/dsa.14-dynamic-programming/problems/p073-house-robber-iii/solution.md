## Approach

Tree DP with the state `(node, mode)` (chapter section 18). Each call returns both modes of its node, and the parent combines its children's pairs in a post-order walk.

- `rob(node) = node.val + skip(left) + skip(right)`: the children are linked to `node`, so they are skipped.
- `skip(node) = max(rob(left), skip(left)) + max(rob(right), skip(right))`: each child does whatever is best for it.
- A missing child gives `(0, 0)`. Answer: `max(rob(root), skip(root))`.

```python
def rob_tree(root):
    def go(node):
        if node is None:
            return 0, 0                           # (rob, skip)
        lrob, lskip = go(node.left)
        rrob, rskip = go(node.right)
        rob = node.val + lskip + rskip
        skip = max(lrob, lskip) + max(rrob, rskip)
        return rob, skip

    return max(go(root))
```

For `[2, 1, 3, None, 4]` (Try it 17): leaves `4 -> (4, 0)` and `3 -> (3, 0)`; node `1 -> (1 + 0, max(4, 0)) = (1, 4)`; root `2 -> (2 + 4 + 0, max(1, 4) + max(3, 0)) = (6, 7)`. Answer 7.

## Complexity

Each node is visited once with `O(1)` work: `O(n)` time. The recursion depth is the height of the tree, `O(h)` memory.

## Another way

`best(node)` = the best for the subtree with no restriction: `max(node.val + best of the four grandchildren, best(left) + best(right))`. It is correct only **with** a memo on the node (`@functools.cache`, nodes are hashable by identity), because each grandchild is reached from its parent and from its grandparent. Without a memo, a chain of `n` nodes makes `fib(n)` calls. The pair version needs no memo at all, because each call already returns everything the parent needs.
