# Trace: which traversal gives this?

Three traversals of the same tree. Predict **exactly** what the program prints. Do not run it.

```python
from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def build_tree(values):
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    return root

def preorder(node):
    if node is None:
        return []
    return [node.val] + preorder(node.left) + preorder(node.right)

def inorder(node):
    if node is None:
        return []
    return inorder(node.left) + [node.val] + inorder(node.right)

def postorder(node):
    if node is None:
        return []
    return postorder(node.left) + postorder(node.right) + [node.val]

root = build_tree([1, 2, 3, 4, None, 5, 6, None, 7])
print("preorder", preorder(root))
print("inorder", inorder(root))
print("postorder", postorder(root))
```

Write your answer in `answer.txt`: three lines, each with the word and the list as printed, for example `preorder [1, 2, 3]`.

## How to work

Draw the tree from `[1, 2, 3, 4, None, 5, 6, None, 7]` with the queue method: the root `1` takes `2` and `3`; `2` takes `4` and a gap; `3` takes `5` and `6`; `4` takes a gap and `7`. Then use the walk around the tree from the chapter (section 4): going once around the outside, write a node the **first** time you touch it for preorder, the **second** time (coming back from the left) for inorder, and the **third** time (leaving it for good) for postorder. Or write the three lists with the rule: node first / node between / node last, one subtree at a time.

## After you answer

1. Which of the three lists starts with the root, and which ends with it?
2. In which list does the node `4` come before the node `2`, and in which does it come after? Why does `7` come right after `4` in two of the lists and right before it in the third?
3. If you were given only the inorder list, could you draw the tree? What more would you need?
