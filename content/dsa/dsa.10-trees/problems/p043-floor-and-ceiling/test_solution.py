import bisect
import random
from collections import deque

import pytest

from solution import TreeNode, floor, ceiling


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


def floor_ceiling_brute(keys, key):
    vals = sorted(keys)
    i = bisect.bisect_right(vals, key)
    j = bisect.bisect_left(vals, key)
    return (vals[i - 1] if i > 0 else None), (vals[j] if j < len(vals) else None)


def test_empty_tree():
    assert floor(None, 5) is None and ceiling(None, 5) is None, "An empty tree has no floor and no ceiling: None."


def test_the_chapter_tree():
    t = make_bst([20, 10, 30, 5, 15, 25, 40])
    cases = [(5, 5, 5), (12, 10, 15), (40, 40, 40), (41, 40, None), (0, None, 5), (22, 20, 25), (29, 25, 30), (100, 40, None)]
    for key, f, c in cases:
        assert floor(t, key) == f, f"floor(t, {key}) should be {f}, got {floor(t, key)}. An exact match is its own floor."
        assert ceiling(t, key) == c, f"ceiling(t, {key}) should be {c}, got {ceiling(t, key)}. An exact match is its own ceiling."


def test_a_single_node():
    t = build([10])
    assert (floor(t, 9), ceiling(t, 9)) == (None, 10), "9 is below the only value 10: floor None, ceiling 10."
    assert (floor(t, 10), ceiling(t, 10)) == (10, 10), "10 is in the tree: it is its own floor and its own ceiling."
    assert (floor(t, 11), ceiling(t, 11)) == (10, None), "11 is above the only value 10: floor 10, ceiling None."


def test_every_key_against_bisect():
    rng = random.Random(43)
    for _ in range(150):
        keys = rng.sample(range(-20, 60), rng.randint(0, 25))
        t = make_bst(keys)
        before = to_level(t)
        for key in range(-23, 63):
            f, c = floor_ceiling_brute(keys, key)
            assert floor(t, key) == f, f"keys {keys}: floor of {key} should be {f}, got {floor(t, key)}."
            assert ceiling(t, key) == c, f"keys {keys}: ceiling of {key} should be {c}, got {ceiling(t, key)}."
        assert to_level(t) == before, "the tree must not change."


def test_it_walks_one_path():
    n = 4095
    keys = list(range(0, 2 * n, 2))                      # even numbers, so the odd ones are missing
    t = build(to_level(balanced_bst(keys)), make=Counting)
    Counting.reads = 0
    got = [(floor(t, k), ceiling(t, k)) for k in (1, 1001, 4001, 8189, 8190, -1)]
    reads = Counting.reads
    assert got == [(0, 2), (1000, 1002), (4000, 4002), (8188, None), (8188, None), (None, 0)], f"unexpected answers {got}."
    assert reads <= 12 * 3 * 13, (
        f"twelve queries read {reads:,} child pointers; one walk down needs about 13 each. "
        "Walk one path using the BST order instead of looking at every node.")
