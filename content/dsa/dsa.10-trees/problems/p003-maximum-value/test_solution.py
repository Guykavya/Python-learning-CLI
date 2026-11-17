import random
from collections import deque

import pytest

from solution import TreeNode, max_value


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


def test_empty_tree_returns_none():
    assert max_value(None) is None, (
        "An empty tree has no largest value: return None (not 0 or -1, which can be real values).")


def test_single_node():
    assert max_value(build([-7])) == -7, "A single node: its own value, even when it is negative."


@pytest.mark.parametrize("values, expected", [
    ([4, 2, 6, 1, 3, 5, 7], 7),
    ([3, 9, 20, None, None, 15, 7], 20),
    ([9, 2, 3], 9),
    ([1, None, 2, None, 3], 3),
    ([-5, -2, -9], -2),
    ([-5, -2, -9, -8, -1], -1),
    ([0, -1, -2], 0),
])
def test_examples(values, expected):
    got = max_value(build(values))
    assert got == expected, (
        f"the largest value of {values} is {expected}, got {got}. If you got 0 for an all-negative tree, "
        "you started with best = 0: start with a real value of the tree. If you got a TypeError, "
        "a child's answer was None and you compared it.")


def test_the_maximum_can_be_in_any_position():
    # the maximum at the root, at a left leaf, at a right leaf, deep on one side
    for values, want in [([9, 1, 2], 9), ([1, 9, 2], 9), ([1, 2, 9], 9), ([1, 2, 3, 4, None, None, None, 9], 9)]:
        got = max_value(build(values))
        assert got == want, f"the largest value of {values} is {want}, got {got}. Look at both subtrees, at every depth."


def test_random_trees():
    rng = random.Random(3)
    for _ in range(200):
        t = random_tree(rng, rng.randint(1, 40), -20, 20)
        want = max(v for v in to_level(t) if v is not None)
        got = max_value(t)
        assert got == want, f"the tree {to_level(t)} has the largest value {want}, but max_value returned {got}."
