## Approach

Keep a `root` and a `size`. `contains` and `insert` are the search loop of section 9; `insert` attaches a new leaf when the walk reaches an empty place. `delete` walks down while remembering the **parent**. With two children, it finds the inorder successor (and the successor's parent), copies the successor's key into the node and from then on removes the successor node, which has no left child. Now exactly one pointer has to change: the parent's `left` or `right` (or `self.root`) gets the removed node's only child, or `None`. `height` uses a stack of `(node, depth)` pairs and `inorder` uses the iterative inorder of section 5, so nothing recurses.

## Code

```python
class BST:
    def __init__(self):
        self.root = None
        self.size = 0

    def __len__(self):
        return self.size

    def contains(self, key):
        cur = self.root
        while cur is not None:
            if key == cur.val:
                return True
            cur = cur.left if key < cur.val else cur.right
        return False

    def insert(self, key):
        if self.root is None:
            self.root = TreeNode(key)
            self.size = 1
            return True
        cur = self.root
        while True:
            if key == cur.val:
                return False                          # already there
            if key < cur.val:
                if cur.left is None:
                    cur.left = TreeNode(key)
                    break
                cur = cur.left
            else:
                if cur.right is None:
                    cur.right = TreeNode(key)
                    break
                cur = cur.right
        self.size += 1
        return True

    def delete(self, key):
        parent, cur = None, self.root
        while cur is not None and cur.val != key:     # find the node and its parent
            parent, cur = cur, (cur.left if key < cur.val else cur.right)
        if cur is None:
            return False
        if cur.left is not None and cur.right is not None:
            succ_parent, succ = cur, cur.right        # two children: the leftmost node of the right subtree
            while succ.left is not None:
                succ_parent, succ = succ, succ.left
            cur.val = succ.val                        # copy its key, then remove the successor node instead
            parent, cur = succ_parent, succ
        child = cur.left if cur.left is not None else cur.right    # at most one child now
        if parent is None:
            self.root = child
        elif parent.left is cur:
            parent.left = child
        else:
            parent.right = child
        self.size -= 1
        return True

    def height(self):
        best = 0
        stack = [(self.root, 1)] if self.root is not None else []
        while stack:
            node, depth = stack.pop()
            best = max(best, depth)
            for child in (node.left, node.right):
                if child is not None:
                    stack.append((child, depth + 1))
        return best

    def inorder(self):
        out, stack, cur = [], [], self.root
        while cur is not None or stack:
            while cur is not None:
                stack.append(cur)
                cur = cur.left
            cur = stack.pop()
            out.append(cur.val)
            cur = cur.right
        return out
```

## Complexity

`insert`, `delete`, `contains`: `O(h)` time, `O(1)` extra memory. `height` and `inorder`: `O(n)` time, `O(h)` memory for the stack (a chain of 2,000 keys is fine: the stack is a Python list, not the call stack). With sorted insertions `h = n`, which is why a plain BST is not enough in practice: a balanced tree (AVL, red-black) keeps `h` near `log n`.

## Another way

Write the same class with recursive helpers (`_insert(node, key)` returning the new subtree root, as in the chapter): it is shorter, and fine for random keys, but it fails on the sorted chain because Python's call stack is about 1,000 frames deep. Or keep `insert` recursive-free and add `rotate` and `rebalance` to make it an AVL tree (section 14); then even sorted keys give a height of about 11 for 2,000 keys.
