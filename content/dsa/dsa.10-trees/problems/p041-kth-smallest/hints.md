## Hint 1

Which traversal visits a BST in increasing order? If you could visit the nodes one by one in that order, which visit is the answer? Do you need to look at the nodes that come after it?

## Hint 2

Use the **iterative inorder** with a stack (section 5): push the left spine, pop one node (this is the next smallest value), then continue with its right child. Keep a counter `k` and decrease it at every pop; when it reaches `0` you hold the answer. If the loop ends first, the tree has fewer than `k` nodes.

## Hint 3

```
stack, cur = [], root
while cur is not None or stack:
    while cur is not None:
        stack.append(cur); cur = cur.left
    cur = stack.pop()
    k -= 1
    if k == 0: return cur.val
    cur = cur.right
return None
```
