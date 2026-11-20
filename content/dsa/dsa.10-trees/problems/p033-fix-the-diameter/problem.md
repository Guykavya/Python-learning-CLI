# Fix the diameter

The **diameter** of a tree is the length of the longest path between any two nodes, counted in **edges**. A classmate wrote this and `starter.py` holds it:

```python
def height(node):
    if node is None:
        return 0
    return 1 + max(height(node.left), height(node.right))

def diameter(root):
    if root is None:
        return 0
    return height(root.left) + height(root.right)
```

It passes their three tests:

```text
[3, 9, 20, None, None, 15, 7]   gives 3   (correct)
[1]                              gives 0   (correct)
[1, 2]                           gives 1   (correct)
```

But the diameter of the tree below is **6**, and their function says 5:

```text
        1
       / \
      2   7
     / \
    3   4
   /     \
  5       8
 /         \
6           9
```

As a level-order list this tree is `[1, 2, 7, 3, 4, None, None, 5, None, None, 8, 6, None, None, 9]`.

1. Which part of the tree does the classmate's function look at? Find a path that is longer than the one it measures and that does **not** pass through the root.
2. Fix the function. Keep the result in **edges**. `O(n)` time: the tests count how often you read a `left` or `right` pointer on a perfect tree of 1,023 nodes, so calling `height` at every node (which walks the same subtrees again and again) fails the count.

## Example

After the fix:

```python
>>> diameter(build([3, 9, 20, None, None, 15, 7]))
3
>>> diameter(build([4, 2, 6, 1, 3, 5, 7]))
4
>>> diameter(build([1]))
0
>>> diameter(None)
0
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes, depth below the recursion limit. `O(n)` time.

## Think about

For every node, the longest path that has this node as its **highest point** goes down the deepest left branch and the deepest right branch. The classmate computes this only for the root. Which number does a parent need from its children, and which number must be **recorded** at every node?
