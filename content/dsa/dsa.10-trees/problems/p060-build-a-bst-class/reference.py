class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


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
