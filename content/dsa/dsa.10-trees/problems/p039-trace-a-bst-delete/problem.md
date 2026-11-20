# Trace: a BST delete

This program builds a binary search tree and then deletes three keys with the three-case `delete` of chapter section 9. Predict **exactly** what it prints. Do not run it.

```python
from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def to_level_list(root):
    if root is None:
        return []
    out, queue = [], deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            out.append(None)
        else:
            out.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out

def inorder(node):
    if node is None:
        return []
    return inorder(node.left) + [node.val] + inorder(node.right)

def insert(root, key):
    if root is None:
        return TreeNode(key)
    if key < root.val:
        root.left = insert(root.left, key)
    elif key > root.val:
        root.right = insert(root.right, key)
    return root

def find_min(root):
    while root.left:
        root = root.left
    return root

def delete(root, key):
    if root is None:
        return None
    if key < root.val:
        root.left = delete(root.left, key)
    elif key > root.val:
        root.right = delete(root.right, key)
    else:
        if root.left is None:
            return root.right
        if root.right is None:
            return root.left
        successor = find_min(root.right)
        root.val = successor.val
        root.right = delete(root.right, successor.val)
    return root

tree = None
for key in (50, 30, 70, 20, 40, 60, 80, 35, 65):
    tree = insert(tree, key)
print("start    :", to_level_list(tree))
for key in (40, 70, 50):
    tree = delete(tree, key)
    print(f"delete {key}:", to_level_list(tree))
print("inorder  :", inorder(tree))
```

Write your answer in `answer.txt`, one printed line per line. The lists are level-order lists: the root first, then its children from left to right, and so on, with `None` for a missing child; the `None`s at the very end are cut off. Mind the spaces: the labels `start    :` and `inorder  :` are padded so that the colons line up, and `delete 40:` has no extra space before the colon.

## How to work

First draw the tree that nine inserts build (each key becomes a new leaf, found by comparing at every node). Then for every delete, name the case before you change anything: does the node have no child, one child, or two? For two children write down the **successor** (the smallest key in the right subtree) before you copy it, and then delete that key from the right subtree. Draw the tree again after each delete, and only then write the level-order list. Two things are easy to get wrong: which node the successor comes from, and what happens to the successor's own child.

## After you answer

1. Which of the three deletes was a one-child case, and which node took the place of the deleted node?
2. In the delete of `70`, why is the successor an easy case, and in the delete of `50` what happens to the right child of the old `60`?
3. The last line is sorted. Why is it sorted after every sequence of deletes, and which mistake would break it?
