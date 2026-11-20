## Approach

An inorder walk of a BST visits the values from smallest to largest, so the k-th visited node holds the answer. Run the iterative inorder (a stack of the nodes whose left subtree is being processed), subtract one from `k` at every visit, and return at the moment `k` reaches `0`. The walk never goes further than needed. If the loop ends, the tree has fewer than `k` nodes and the answer is `None`.

## Code

```python
def kth_smallest(root, k):
    stack, cur = [], root
    while cur is not None or stack:
        while cur is not None:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        k -= 1
        if k == 0:
            return cur.val
        cur = cur.right
    return None                                    # fewer than k nodes
```

## Complexity

`O(h + k)` time: `h` steps to reach the smallest node, then `k` visits (each node is pushed and popped at most once). `O(h)` memory for the stack.

## Another way

If you must answer many k-th queries on a tree that changes, store the **size of each subtree** in every node. At a node compare `k` with the size of the left subtree: go left, return this node, or go right with `k` reduced. That costs `O(h)` per query (an *order-statistic tree*).
