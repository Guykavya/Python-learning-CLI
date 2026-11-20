import random
from collections import deque

import pytest

from solution import TreeNode, is_balanced


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


def heights_ok(node):
    """The test's own slow check: (balanced?, height), recursive, only for small trees."""
    if node is None:
        return True, 0
    ok_l, hl = heights_ok(node.left)
    ok_r, hr = heights_ok(node.right)
    return ok_l and ok_r and abs(hl - hr) <= 1, 1 + max(hl, hr)


def test_empty_and_single():
    assert is_balanced(None) is True, "An empty tree is balanced."
    assert is_balanced(build([1])) is True, "A single node is balanced."


@pytest.mark.parametrize("values, expected", [
    ([3, 9, 20, None, None, 15, 7], True),
    ([1, 2, 3, 4, 5, 6, 7], True),
    ([1, 2], True),
    ([1, 2, None, 3], False),
    ([1, None, 2, None, 3], False),
    ([1, 2, 2, 3, 3, None, None, 4, 4], False),
    ([1, 2, 2, 3, None, None, 3, 4, None, None, 4], False),
    ([1, 2, 3, 4, None, None, 5], True),
    ([1, 2, 3, 4, 5, 6, None, 7], True),
    ([1, 2, 3, 4, 5, None, None, 6], False),
])
def test_examples(values, expected):
    got = is_balanced(build(values))
    assert got is expected, (
        f"is_balanced({values}) should be {expected}, got {got}. The heights of the two sides of EVERY node may "
        "differ by at most 1, not only at the root.")


def test_the_root_looks_fine_but_a_node_below_is_not():
    got = is_balanced(build([1, 2, 2, 3, None, None, 3, 4, None, None, 4]))
    assert got is False, (
        "[1, 2, 2, 3, None, None, 3, 4, None, None, 4]: both sides of the root have height 3, but the node 2 on the "
        f"left has a left subtree of height 2 and no right subtree, so the tree is not balanced; got {got}. "
        "Check every node, not only the root.")


def test_random_trees_against_the_slow_check():
    rng = random.Random(26)
    for _ in range(300):
        t = random_tree(rng, rng.randint(0, 14))
        want = heights_ok(t)[0]
        got = is_balanced(t)
        assert got is want, f"the tree {to_level(t)}: is_balanced should be {want}, got {got}."


def test_it_is_one_pass_not_a_height_call_at_every_node():
    n = 4095                                          # a perfect tree: 12 levels
    t = build(list(range(1, n + 1)), make=Counting)
    Counting.reads = 0
    got = is_balanced(t)
    reads = Counting.reads
    assert got is True, "a perfect tree is balanced."
    assert reads <= 8 * n, (
        f"your function read {reads:,} child pointers on a tree of {n:,} nodes; one pass needs only about {2 * n:,}. "
        "You probably call a height function at every node, which walks the same subtrees again and again "
        "(O(n log n) here, O(n^2) on a chain). Return the height from the same recursive call that checks the balance.")
