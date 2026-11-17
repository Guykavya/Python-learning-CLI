import random
from collections import deque

import pytest

from solution import TreeNode, values_at_depth


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


def levels_of(root):
    """The test's own level-order walk: a list of levels, each a list of values (the brute force)."""
    out, level = [], ([root] if root is not None else [])
    while level:
        out.append([n.val for n in level])
        level = [c for n in level for c in (n.left, n.right) if c is not None]
    return out


def test_empty_tree():
    assert values_at_depth(None, 0) == [], "An empty tree has no nodes at any depth: return []."
    assert values_at_depth(None, 3) == [], "An empty tree has no nodes at any depth: return []."


def test_depth_zero_is_the_root():
    assert values_at_depth(build([8, 1, 2]), 0) == [8], "Depth 0 is only the root: [8]."


@pytest.mark.parametrize("d, expected", [(0, [3]), (1, [9, 20]), (2, [15, 7]), (3, []), (10, [])])
def test_example_tree(d, expected):
    t = build([3, 9, 20, None, None, 15, 7])
    got = values_at_depth(t, d)
    assert got == expected, (
        f"depth {d} of [3, 9, 20, None, None, 15, 7] is {expected}, got {got}. "
        "Return [] below the leaves, and keep the left-to-right order.")


def test_left_to_right_order_with_gaps():
    t = build([1, 2, 3, None, 4, 5, None])     # level 2 holds 4 (right child of 2) and 5 (left child of 3)
    assert values_at_depth(t, 2) == [4, 5], "Level 2 is [4, 5]: the left subtree's nodes come before the right subtree's."


def test_all_depths_of_random_trees():
    rng = random.Random(9)
    for _ in range(100):
        t = random_tree(rng, rng.randint(0, 30))
        levels = levels_of(t)
        for d in range(len(levels) + 3):
            want = levels[d] if d < len(levels) else []
            got = values_at_depth(t, d)
            assert got == want, f"in the tree {to_level(t)} the values at depth {d} are {want}, got {got}."
