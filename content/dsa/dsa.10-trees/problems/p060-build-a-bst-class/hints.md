## Hint 1

Start with the easy loops. `contains` walks down: equal means found, smaller goes left, larger goes right, falling off means not found. `insert` walks the same way, but when it reaches an empty place on the left or right of a node, it puts a new `TreeNode` there. Keep a counter `size` in the object. What does `insert` return for a key that is already there?

## Hint 2

`delete` needs the **parent** of the node. Walk down keeping `parent` and `cur`. If `cur` has two children, find its successor (the leftmost node of its right subtree) while remembering the successor's parent, copy the successor's key into `cur`, and then delete the successor node instead: it has no left child. Now the node to remove has at most one child: let `parent` point to that child instead of the node (check whether the node was `parent.left` or `parent.right`; if `parent` is `None`, the child becomes `self.root`).

## Hint 3

`height`: a stack of pairs.

```
best = 0
stack = [(self.root, 1)] if self.root is not None else []
while stack:
    node, depth = stack.pop()
    best = max(best, depth)
    for child in (node.left, node.right):
        if child is not None: stack.append((child, depth + 1))
return best
```

`inorder`: the iterative inorder with a stack (section 5), returning a new list.
