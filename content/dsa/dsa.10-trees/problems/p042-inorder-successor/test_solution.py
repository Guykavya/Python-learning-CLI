import random
from collections import deque

import pytest

from solution import TreeNode, successor


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


def test_empty_tree():
    assert successor(None, 5) is None, "An empty tree has no successor: return None."


def test_the_chapter_tree():
    t = make_bst([20, 10, 30, 5, 15, 25, 40])
    cases = [(5, 10), (10, 15), (12, 15), (15, 20), (20, 25), (25, 30), (30, 40), (40, None), (41, None), (0, 5), (-9, 5)]
    for key, want in cases:
        got = successor(t, key)
        assert got == want, (
            f"successor(t, {key}) should be {want}, got {got}. "
            "Remember the node you leave behind every time you go left; a key without a right subtree "
            "(like 15 or 25) has its successor ABOVE it.")


def test_a_key_that_is_not_in_the_tree_and_a_single_node():
    t = build([7])
    assert successor(t, 7) is None, "the only value is 7: nothing is strictly larger."
    assert successor(t, 6) == 7 and successor(t, 8) is None, "6 -> 7; 8 has no successor."
    t = make_bst([10, 5, 15])
    assert successor(t, 11) == 15 and successor(t, 14) == 15, "a key between two values gets the next larger value."


def test_every_key_against_a_sorted_list():
    rng = random.Random(42)
    for _ in range(150):
        keys = rng.sample(range(0, 60), rng.randint(0, 25))
        t = make_bst(keys)
        vals = sorted(keys)
        before = to_level(t)
        for key in range(-2, 63):
            bigger = [v for v in vals if v > key]
            want = bigger[0] if bigger else None
            got = successor(t, key)
            assert got == want, f"keys {keys}: successor of {key} should be {want}, got {got}."
        assert to_level(t) == before, "the tree must not change."


def test_it_walks_one_path():
    n = 4095
    t = build(to_level(balanced_bst(list(range(n)))), make=Counting)
    Counting.reads = 0
    got = [successor(t, key) for key in (0, 1000, 2047, 4093, 4094, -5)]
    reads = Counting.reads
    assert got == [1, 1001, 2048, 4094, None, 0], f"successors of 0, 1000, 2047, 4093, 4094, -5 should be [1, 1001, 2048, 4094, None, 0], got {got}."
    assert reads <= 6 * 3 * 13, (
        f"six queries read {reads:,} child pointers; one walk down needs about 13 each. "
        "Do not build the inorder list: one loop from the root is enough.")
