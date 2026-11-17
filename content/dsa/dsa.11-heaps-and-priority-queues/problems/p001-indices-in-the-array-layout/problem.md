# Indices in the array layout

A binary heap is stored in a plain list, level by level, **starting at index 0** (chapter section 2):

```text
index:   0   1   2   3   4   5   6
value: [ 1,  3,  2,  7,  4,  5,  6 ]

           1            index 0
         /   \
        3     2         indexes 1 and 2
       / \   / \
      7   4 5   6       indexes 3, 4, 5, 6
```

Write four small functions. They work on **indexes**, not on values, so they do not receive the list.

- `parent(i)` returns the index of the parent of the node at index `i`. It is only asked for `i >= 1` (the root has no parent).
- `left(i)` returns the index of the left child of `i`.
- `right(i)` returns the index of the right child of `i`.
- `children(i, n)` returns a **list** with the indexes of the children of `i` that really exist in a heap of `n` items: the left child first, then the right one. A child exists only when its index is **smaller than `n`**. A leaf gives `[]`.

## Example

```python
>>> parent(5)
2
>>> left(1), right(1)
(3, 4)
>>> children(1, 7)      # the node with value 3 in the picture
[3, 4]
>>> children(2, 6)      # index 6 does not exist when the heap has 6 items
[5]
>>> children(3, 7)      # a leaf
[]
```

## Constraints

- Use plain integer arithmetic. Every function is a single line.
- `parent` must give an `int` (not `2.0`).
- `0 <= i`, `1 <= n <= 10**6`.

## Think about

Why does the layout need no pointers at all? Check with the picture: the children of index 2 are 5 and 6, and the parent of both is 2. If your `parent(left(i))` is not `i` for every `i`, one of the formulas is wrong.
