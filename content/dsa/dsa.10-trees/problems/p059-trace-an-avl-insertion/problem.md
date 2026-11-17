# Trace: an AVL insertion

This is the AVL tree of chapter section 14, with a `print` at the start of each rotation and one line after each insertion. Predict **exactly** what it prints. Do not run it.

```python
from collections import deque

class AVLNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
        self.height = 1

def h(node):
    return node.height if node else 0

def update(node):
    node.height = 1 + max(h(node.left), h(node.right))

def balance_factor(node):
    return h(node.left) - h(node.right)

def rotate_right(y):
    print(f"rotate_right at {y.val}")
    x = y.left
    y.left = x.right
    x.right = y
    update(y)
    update(x)
    return x

def rotate_left(x):
    print(f"rotate_left at {x.val}")
    y = x.right
    x.right = y.left
    y.left = x
    update(x)
    update(y)
    return y

def rebalance(node):
    update(node)
    balance = balance_factor(node)
    if balance > 1:
        if balance_factor(node.left) < 0:
            node.left = rotate_left(node.left)
        return rotate_right(node)
    if balance < -1:
        if balance_factor(node.right) > 0:
            node.right = rotate_right(node.right)
        return rotate_left(node)
    return node

def avl_insert(node, key):
    if node is None:
        return AVLNode(key)
    if key < node.val:
        node.left = avl_insert(node.left, key)
    elif key > node.val:
        node.right = avl_insert(node.right, key)
    else:
        return node
    return rebalance(node)

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

root = None
for key in (10, 20, 30, 40, 50, 25):
    root = avl_insert(root, key)
    print(f"insert {key}: {to_level_list(root)}")
print("height:", root.height)
```

Write your answer in `answer.txt`, one printed line per line. A `rotate_...` line is printed **while** the insertion runs, so it comes **before** the `insert ...` line of the same key. The list after `insert` is the level-order list of the tree after that insertion (with `None` for gaps; the `None`s at the very end are cut off). The last line is the stored height of the root.

## How to work

For each key: insert it as a new leaf like in an ordinary BST, then go back **up the path** you came down, and at every node on that path (lowest first) recompute the height and the balance factor `h(left) - h(right)`. The first node where the factor is `2` or `-2` needs a rotation. Decide the case: the factor `-2` with a right child that is not left-heavy needs one left rotation; the factor `-2` with a right child that is left-heavy needs a right rotation on the child first (this prints **two** lines). Draw the tree after every key before you write its list, and write down the height of every node on the path.

## After you answer

1. Which of the insertions needed a single rotation, and which a double rotation? Name the case (left-left, right-right, left-right, right-left) for each.
2. After the insertion of `25`, which node was the first one on the way up that was out of balance? Why did the nodes `30` and `40` below it not need a rotation?
3. How tall would the tree be if the same six keys were inserted into an ordinary BST?
