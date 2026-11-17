# Build a BST class with tests

Put everything of chapter section 9 into one class. `BST` stores distinct keys in a binary search tree made of `TreeNode` objects (the class is in your file). It must have:

| Method | Does |
|---|---|
| `insert(key)` | add `key`; return `True` if it was added, `False` if it was already in the tree |
| `delete(key)` | remove `key` (leaf, one child, or two children with the inorder **successor**); return `True` if it was removed, `False` if it was not in the tree |
| `contains(key)` | `True` or `False` |
| `height()` | the number of nodes on the longest path from the root to a leaf; `0` for an empty tree |
| `inorder()` | a **new list** of all keys in increasing order |
| `__len__()` | the number of keys (so `len(tree)` works) |

**All methods must be loops, not recursion.** Inserting the keys `1, 2, 3, ..., 2000` in sorted order makes a chain 2,000 nodes deep, and a recursive method runs out of stack. The tests run these chains with the recursion limit lowered, and they compare thousands of random operations with a Python `set`. Keep the keys **in the tree**: the file may not use `set`, `sorted`, `bisect`, or `sys.setrecursionlimit`.

## Example

```python
>>> tree = BST()
>>> [tree.insert(k) for k in (5, 3, 8, 1, 4, 7, 9, 2)]
[True, True, True, True, True, True, True, True]
>>> tree.insert(4), len(tree), tree.height()
(False, 8, 4)
>>> tree.inorder()
[1, 2, 3, 4, 5, 7, 8, 9]
>>> tree.delete(5), tree.delete(42), tree.contains(5), tree.contains(7)
(True, False, False, True)
>>> tree.inorder(), len(tree), tree.height()
([1, 2, 3, 4, 7, 8, 9], 7, 4)
```

## Constraints

- Sorted insertions of 2,000 keys must work, each method in `O(h)` time (`O(n)` for `inorder`). No recursion in any method.

## Think about

Write the **tests first** for each method, from the cases of the chapter (a leaf, one child, two children, a missing key, an empty tree). Which methods are easy as loops (`contains`, `insert`)? What do you need to remember while you walk down in `delete`, so that you can change the parent's pointer without recursion? How do you count the height without recursion (a stack of pairs `(node, depth)`, or a queue by levels)?
