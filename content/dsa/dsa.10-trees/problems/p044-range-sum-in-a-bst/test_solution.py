import random
from collections import deque

import pytest

from solution import TreeNode, range_sum


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
    assert range_sum(None, 0, 5) == 0, "An empty tree has no values: the sum is 0."


@pytest.mark.parametrize("keys, lo, hi, expected", [
    ([10, 5, 15, 3, 7, 18], 7, 15, 32),
    ([10, 5, 15, 3, 7, 18], 6, 10, 17),
    ([10, 5, 15, 3, 7, 18], 20, 30, 0),
    ([10, 5, 15, 3, 7, 18], 0, 100, 58),
    ([10, 5, 15, 3, 7, 18], 10, 10, 10),
    ([10, 5, 15, 3, 7, 18], 11, 14, 0),
    ([7], 7, 7, 7),
    ([7], 8, 9, 0),
])
def test_examples(keys, lo, hi, expected):
    got = range_sum(make_bst(keys), lo, hi)
    assert got == expected, (
        f"BST from {keys}, range [{lo}, {hi}]: the sum should be {expected}, got {got}. Both ends are included.")


def test_negative_values():
    t = make_bst([0, -5, 5, -8, -2, 3, 9])
    assert range_sum(t, -5, 3) == -5 + -2 + 0 + 3, "values -5, -2, 0, 3 are in the range [-5, 3]: sum -4."
    assert range_sum(t, -100, -1) == -5 - 8 - 2, "the range [-100, -1] holds -8, -5 and -2."


def test_random_trees_against_a_plain_sum():
    rng = random.Random(44)
    for _ in range(300):
        keys = rng.sample(range(-30, 60), rng.randint(0, 30))
        t = make_bst(keys)
        lo = rng.randint(-35, 55)
        hi = lo + rng.randint(0, 40)
        want = sum(k for k in keys if lo <= k <= hi)
        got = range_sum(t, lo, hi)
        assert got == want, f"keys {keys}, range [{lo}, {hi}]: the sum should be {want}, got {got}."


def test_it_skips_subtrees_that_cannot_hold_the_range():
    n = 4095
    t = build(to_level(balanced_bst(list(range(n)))), make=Counting)
    Counting.reads = 0
    got = range_sum(t, 1000, 1010)
    reads = Counting.reads
    assert got == sum(range(1000, 1011)), f"the sum of 1000..1010 is {sum(range(1000, 1011))}, got {got}."
    assert reads <= 400, (
        f"your function read {reads:,} child pointers for a range of 11 values in a tree of 4,095 nodes "
        "(a function that visits every node reads about 8,000; a pruned one about 70). "
        "If the node is below lo skip its LEFT subtree; if it is above hi skip its RIGHT subtree.")
    Counting.reads = 0
    got = range_sum(t, 0, n)
    assert got == sum(range(n)), "the whole tree is in the range: the sum of 0..4094."
