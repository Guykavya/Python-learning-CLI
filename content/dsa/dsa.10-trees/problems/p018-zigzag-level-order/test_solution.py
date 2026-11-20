import random
from collections import deque

import pytest

from solution import TreeNode, zigzag


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
    assert zigzag(None) == [], "An empty tree has no levels: []."


def test_single_node():
    assert zigzag(build([8])) == [[8]], "The root level is left to right: [[8]]."


@pytest.mark.parametrize("values, expected", [
    ([1, 2, 3, 4, 5, 6, 7], [[1], [3, 2], [4, 5, 6, 7]]),
    ([3, 9, 20, None, None, 15, 7], [[3], [20, 9], [15, 7]]),
    ([1, 2, 3], [[1], [3, 2]]),
    ([1, 2, None, 3, None, 4], [[1], [2], [3], [4]]),
    ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
     [[1], [3, 2], [4, 5, 6, 7], [15, 14, 13, 12, 11, 10, 9, 8]]),
])
def test_examples(values, expected):
    got = zigzag(build(values))
    assert got == expected, (
        f"zigzag of {values} should be {expected}, got {got}. Levels 0, 2, 4 are left to right; "
        "levels 1, 3, 5 are right to left. Reverse the finished level; do not change the queue order.")


def test_third_level_is_left_to_right_again():
    got = zigzag(build([1, 2, 3, 4, 5, 6, 7]))
    assert got[2] == [4, 5, 6, 7], f"level 2 must be left to right again: [4, 5, 6, 7], got {got[2]}. Reverse only the odd levels."


def test_random_trees_against_the_levels_walk():
    rng = random.Random(18)
    for _ in range(200):
        t = random_tree(rng, rng.randint(0, 40))
        want = [lv[::-1] if i % 2 else lv for i, lv in enumerate(levels_of(t))]
        got = zigzag(t)
        assert got == want, f"zigzag of {to_level(t)} should be {want}, got {got}."
