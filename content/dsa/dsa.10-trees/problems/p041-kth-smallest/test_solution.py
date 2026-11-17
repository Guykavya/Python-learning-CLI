import random
from collections import deque

import pytest

from solution import TreeNode, kth_smallest


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


def test_empty_tree_and_too_large_k():
    assert kth_smallest(None, 1) is None, "An empty tree has no k-th value: return None."
    t = make_bst([5, 3, 6, 2, 4, 1])
    assert kth_smallest(t, 7) is None, "the tree has 6 values, so k = 7 has no answer: return None."
    assert kth_smallest(t, 100) is None, "k much larger than the size: return None."


def test_every_k_in_a_small_tree():
    keys = [5, 3, 6, 2, 4, 1]
    t = make_bst(keys)
    for k in range(1, 7):
        got = kth_smallest(t, k)
        assert got == sorted(keys)[k - 1], (
            f"kth_smallest(t, {k}) should be {sorted(keys)[k - 1]}, got {got}. k = 1 is the SMALLEST value; "
            "check your counter for an off-by-one.")


@pytest.mark.parametrize("keys, k, expected", [
    ([3, 1, 4, 2], 1, 1),
    ([3, 1, 4, 2], 4, 4),
    ([7], 1, 7),
    ([-5, -10, 0], 1, -10),
    ([0], 1, 0),
])
def test_small_examples(keys, k, expected):
    got = kth_smallest(make_bst(keys), k)
    assert got == expected, f"BST from {keys}: the {k}-th smallest is {expected}, got {got}."


def test_random_trees_against_a_sorted_list_and_the_tree_is_unchanged():
    rng = random.Random(41)
    for _ in range(150):
        keys = rng.sample(range(-40, 80), rng.randint(1, 30))
        t = make_bst(keys)
        before = to_level(t)
        for k in range(1, len(keys) + 2):
            want = sorted(keys)[k - 1] if k <= len(keys) else None
            got = kth_smallest(t, k)
            assert got == want, f"keys {keys}: k = {k} should give {want}, got {got}."
        assert to_level(t) == before, "finding the k-th value must not change the tree."


def test_two_calls_in_a_row():
    t = make_bst([5, 3, 6, 2, 4, 1])
    assert kth_smallest(t, 2) == 2 and kth_smallest(t, 2) == 2, (
        "the same call twice must give the same answer: keep the counter inside the function.")


def test_it_stops_early():
    n = 4095                                           # a perfect BST: 12 levels
    t = build(to_level(balanced_bst(list(range(n)))), make=Counting)
    for k, limit in ((1, 100), (3, 130), (100, 800)):
        Counting.reads = 0
        got = kth_smallest(t, k)
        reads = Counting.reads
        assert got == k - 1, f"the keys are 0..4094, so the {k}-th smallest is {k - 1}, got {got}."
        assert reads <= limit, (
            f"kth_smallest(t, {k}) read {reads:,} child pointers on a tree of 4,095 nodes; about {2 * (k + 12)} are enough. "
            "Do not build the whole inorder list: count the visits and return at the k-th one.")
