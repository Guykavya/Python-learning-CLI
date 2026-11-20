import random
from collections import deque

import pytest

from solution import TreeNode, lca_bst


def build(values, make=None):
    """Level-order list (None = no node here) -> tree. Uses a queue, never recursion, so deep trees are fine."""
    make = make or TreeNode
    if not values or values[0] is None:
        return None
    root = make(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values) and values[i] is not None:
            node.left = make(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = make(values[i])
            queue.append(node.right)
        i += 1
    return root


def to_level(root):
    """Tree -> level-order list with None for gaps (trailing Nones removed).
    A node reached twice (a cycle or a shared node) stops the walk with a message instead of hanging."""
    if root is None:
        return []
    out, queue, seen = [], deque([root]), set()
    while queue:
        node = queue.popleft()
        if node is None:
            out.append(None)
            continue
        if id(node) in seen:
            raise AssertionError(
                f"the tree has a cycle or a shared node: the node with value {node.val!r} is reachable twice. "
                "Some left/right pointer points back to a node that is already in the tree.")
        seen.add(id(node))
        out.append(node.val)
        queue.append(node.left)
        queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


def nodes(root):
    """All node objects of the tree, parents before children (a plain loop; stops on a cycle)."""
    out, stack, seen = [], ([root] if root is not None else []), set()
    while stack:
        node = stack.pop()
        if id(node) in seen:
            raise AssertionError(
                f"the tree has a cycle or a shared node: the node with value {node.val!r} is reachable twice.")
        seen.add(id(node))
        out.append(node)
        for child in (node.right, node.left):
            if child is not None:
                stack.append(child)
    return out


def short(seq, n=12):
    """A list for a failure message, cut after n items."""
    seq = list(seq)
    text = repr(seq[:n])
    return text if len(seq) <= n else text[:-1] + f", ... {len(seq)} items]"


def random_tree(rng, n, lo=0, hi=9):
    """A random binary tree with n nodes and random values in [lo, hi] (the chapter's helper)."""
    if n == 0:
        return None
    root = TreeNode(rng.randint(lo, hi))
    free = [(root, "left"), (root, "right")]              # empty child slots
    for _ in range(n - 1):
        i = rng.randrange(len(free))
        free[i], free[-1] = free[-1], free[i]
        node, side = free.pop()
        child = TreeNode(rng.randint(lo, hi))
        setattr(node, side, child)
        free += [(child, "left"), (child, "right")]
    return root


class Counting(TreeNode):
    """A TreeNode that counts how often its left and right pointers are READ (assigning is free)."""
    reads = 0

    def __init__(self, val=0, left=None, right=None):
        self._left = None
        self._right = None
        super().__init__(val, left, right)

    @property
    def left(self):
        Counting.reads += 1
        return self._left

    @left.setter
    def left(self, node):
        self._left = node

    @property
    def right(self):
        Counting.reads += 1
        return self._right

    @right.setter
    def right(self, node):
        self._right = node


def insert_ref(root, key):
    """The test's own BST insert (a loop, duplicates ignored). Returns the root."""
    node = TreeNode(key)
    if root is None:
        return node
    cur = root
    while True:
        if key == cur.val:
            return root
        side = "left" if key < cur.val else "right"
        nxt = getattr(cur, side)
        if nxt is None:
            setattr(cur, side, node)
            return root
        cur = nxt


def make_bst(keys):
    """A BST made by inserting the keys one after the other (the shape depends on the order)."""
    root = None
    for k in keys:
        root = insert_ref(root, k)
    return root


def balanced_bst(keys, make=TreeNode):
    """A BST of minimal height for the SORTED list `keys` (the middle key is the root)."""
    def go(lo, hi):
        if lo >= hi:
            return None
        mid = (lo + hi) // 2
        return make(keys[mid], go(lo, mid), go(mid + 1, hi))
    return go(0, len(keys))


def inorder_vals(root):
    """The test's own inorder walk (a loop with a stack)."""
    out, stack, cur = [], [], root
    while cur is not None or stack:
        while cur is not None:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        out.append(cur.val)
        cur = cur.right
    return out


def is_bst_ref(root):
    """True if the inorder values are strictly increasing."""
    vals = inorder_vals(root)
    return all(a < b for a, b in zip(vals, vals[1:]))


def parent_ids(root):
    """{id(node): parent node or None} for every node (a plain loop; the test's own helper)."""
    parent = {id(root): None}
    for node in nodes(root):
        for child in (node.left, node.right):
            if child is not None:
                parent[id(child)] = node
    return parent


def brute_lca(root, p, q):
    """The lowest node on the path root -> q that is also on the path root -> p (parent links, no recursion)."""
    parent = parent_ids(root)
    above_p, cur = set(), p
    while cur is not None:
        above_p.add(id(cur))
        cur = parent[id(cur)]
    cur = q
    while id(cur) not in above_p:
        cur = parent[id(cur)]
    return cur


def by_value(root):
    """{value: node} for a tree with distinct values."""
    return {n.val: n for n in nodes(root)}


def test_the_chapter_tree():
    t = make_bst([20, 10, 30, 5, 15, 25, 40])
    n = by_value(t)
    cases = [(5, 15, 10), (5, 10, 10), (25, 40, 30), (5, 40, 20), (10, 40, 20), (20, 5, 20), (15, 25, 20), (5, 5, 5)]
    for a, b, want in cases:
        got = lca_bst(t, n[a], n[b])
        assert got is n[want], (
            f"the LCA of {a} and {b} should be {want}, got {'None' if got is None else got.val}. "
            "Go left if both are smaller, right if both are larger; stop at the first node that splits them "
            "or that equals one of them.")


def test_single_node_and_a_chain():
    one = build([4])
    assert lca_bst(one, one, one) is one, "a single node: the LCA of the node with itself is the node."
    t = make_bst(range(1, 301))                       # a right chain 1 -> 2 -> ... -> 300 (sorted insertion)
    n = by_value(t)
    assert lca_bst(t, n[300], n[150]) is n[150], "on a chain the smaller key is the ancestor of the larger one."
    assert lca_bst(t, n[1], n[300]) is n[1], "the root is the LCA of the root and any node."


def test_random_bsts_against_the_parent_map():
    rng = random.Random(48)
    for _ in range(400):
        keys = rng.sample(range(100), rng.randint(1, 25))
        t = make_bst(keys)
        all_ = nodes(t)
        p, q = rng.choice(all_), rng.choice(all_)
        want = brute_lca(t, p, q)
        got = lca_bst(t, p, q)
        assert got is want, (
            f"keys inserted in this order: {keys}. The LCA of {p.val} and {q.val} is {want.val}, "
            f"got {'None' if got is None else got.val}.")


def test_it_walks_one_path():
    n = 4095
    t = build(to_level(balanced_bst(list(range(n)))), make=Counting)
    by_key = {node.val: node for node in nodes(t)}
    Counting.reads = 0
    got = [lca_bst(t, by_key[a], by_key[b]).val for a, b in ((0, 1), (1000, 1010), (4093, 4094), (7, 4000), (2047, 2047))]
    reads = Counting.reads
    assert got == [1, 1007, 4093, 2047, 2047], (
        f"unexpected answers {got}; the LCA of (0, 1) is 1 (the leaf 0 is a child of 1), of (1000, 1010) is 1007, of (4093, 4094) is 4093, "
        "of (7, 4000) is 2047 and of 2047 with itself is 2047.")
    assert reads <= 5 * 2 * 13, (
        f"five queries read {reads:,} child pointers; one walk down needs about 13 each. "
        "Use the order: do not search both subtrees.")
