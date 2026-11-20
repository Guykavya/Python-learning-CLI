## Model answer

`size(node)` returns the **number of nodes** in the tree that starts at `node`. `height(node)` returns the **number of nodes on the longest downward path** from `node` (we count nodes, not edges). `count_leaves(node)` returns the **number of leaves**, nodes without children, in the tree that starts at `node`. `is_leaf(node)` answers a yes/no question about the single node.

For `None` the base value must be what the question means for a tree with **no nodes**. An empty tree has `0` nodes, so `size(None) = 0`. It has no path at all, so `height(None) = 0` (the empty path). It has `0` leaves, so `count_leaves(None) = 0`. And `is_leaf(None)` is `False`, because there is no node that could be a leaf; an empty child is only "nothing here". If it returned `True`, every missing child would be counted as a leaf, which gives `n + 1` extra leaves.

For a single node the answers come from the recursive line with two empty children: `size = 1 + 0 + 0 = 1`, `height = 1 + max(0, 0) = 1`. For `count_leaves` it is the second base case: the node has no children, so `is_leaf` is true and the function returns `1` without recursing.

If the `is_leaf` case is deleted, `count_leaves` can only return sums of `0`s: the recursion ends in `None`, and `None` returns `0`, so the function returns `0` for every tree. Something has to produce a `1` before the recursion reaches `None`; that is the job of the leaf case.

`max_value(None)` cannot return `0`, because `0` is a legal value: for a tree of negative numbers the answer `0` would beat every real value, and the caller could not tell "empty" from "the maximum is 0". It should return `None`, and then the combining code must **skip** a `None` answer from a child (check `is not None` before comparing) and start from the node's own value.

The rule for the base case: choose the value that is **correct for the sentence**, the answer for a tree with no nodes, and that does not disturb the combining step (0 for sums and counts, `None` or negative infinity for a maximum).

Checklist: your answer should mention
- [ ] each function's meaning in words: a count of nodes, a path length in nodes, a count of leaves
- [ ] the base case for `None` follows from the meaning: 0 nodes, an empty path, 0 leaves
- [ ] `is_leaf(None)` is `False`: an empty child is not a node, so it is not a leaf
- [ ] a single node: `1 + 0 + 0` and `1 + max(0, 0)`, and the leaf case for `count_leaves`
- [ ] without the leaf case `count_leaves` returns 0 for every tree, because the recursion only ends in `None`
- [ ] `max_value(None)` returns `None`, not `0`, because `0` can be a real value
- [ ] the combining step must skip or handle the `None` answer
- [ ] the rule: the base value is the answer for "no nodes" and must be neutral for the combining step
