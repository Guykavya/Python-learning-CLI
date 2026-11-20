## Hint 1

You already have the iterative inorder of problem 13: it pushes the left path, pops, visits, moves right. What changes if "visit" means **hand the value to the caller and wait**? Which Python keyword does that?

## Hint 2

Replace `out.append(cur.val)` by `yield cur.val`. The stack and `cur` are local variables of the generator, so they keep their values while the generator is paused between two `next()` calls. No list is built.

## Hint 3

```
stack, cur = [], root
while cur is not None or stack:
    while cur is not None:
        stack.append(cur)
        cur = cur.left
    cur = stack.pop()
    yield cur.val
    cur = cur.right
```
(The recursive way: `yield from iter_inorder(node.left)`, `yield node.val`, `yield from iter_inorder(node.right)`.)
