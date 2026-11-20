## Approach

Take the iterative inorder of problem 13 and replace "append to a list" by `yield`. The state of the walk (the stack and `cur`) lives in the local variables of the generator, which Python keeps while the generator is paused. To produce the first value the generator pushes the left path (`O(h)` steps) and pops once; every later `next()` does only the steps up to the next visit. The caller pays only for the values it takes.

## Code

```python
def iter_inorder(root):
    stack, cur = [], root
    while cur is not None or stack:
        while cur is not None:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        yield cur.val
        cur = cur.right
```

## Complexity

Taking `k` values costs `O(h + k)` pointer reads: the first `next()` pushes the left path (`h` pushes), and every later pop, together with the pushes it triggers on a right subtree, is paid for by the value it produces. Extra memory is `O(h)`. Producing all `n` values is `O(n)` in total.

## Another way

A recursive generator is shortest and is the chapter's version (section 4):

```python
def iter_inorder(root):
    if root is None:
        return
    yield from iter_inorder(root.left)
    yield root.val
    yield from iter_inorder(root.right)
```

It is also lazy, but each value travels through up to `h` nested generators, so one `next()` costs `O(h)`, and a skewed tree with thousands of nodes hits the recursion limit. The stack version has neither problem. The same idea, an iterator that pauses between nodes, is the BST iterator of problem 45.
