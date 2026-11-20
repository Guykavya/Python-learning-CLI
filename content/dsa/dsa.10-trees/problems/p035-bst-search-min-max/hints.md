## Hint 1

Compare `key` with the value of the current node. If they are equal, you found it. If `key` is smaller, can the key be in the right subtree? Which single child do you move to? What does "falling off the tree" (reaching `None`) tell you?

## Hint 2

`find_min` needs no key at all: the smallest value is the **leftmost** node, so keep going left as long as there is a left child. `find_max` is the mirror image. For an empty tree return `None` before you start going down.

## Hint 3

```
search(root, key):
    cur = root
    while cur is not None:
        if key == cur.val: return cur
        cur = cur.left if key < cur.val else cur.right
    return None

find_min(root):
    if root is None: return None
    while root.left is not None: root = root.left
    return root
```
