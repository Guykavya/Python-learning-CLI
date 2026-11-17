import random
from collections import deque

import pytest

from solution import TreeNode, right_side_view


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
    assert right_side_view(None) == [], "An empty tree shows nothing: []."


def test_single_node():
    assert right_side_view(build([4])) == [4], "A single node is the only thing you see: [4]."


@pytest.mark.parametrize("values, expected", [
    ([1, 2, 3, None, 5, None, 4], [1, 3, 4]),
    ([1, 2, 3, 4], [1, 3, 4]),
    ([1, None, 3], [1, 3]),
    ([1, 2], [1, 2]),
    ([1, 2, None, 3, None, 4], [1, 2, 3, 4]),
    ([1, 2, 3, 4, 5, 6, 7], [1, 3, 7]),
])
def test_examples(values, expected):
    got = right_side_view(build(values))
    assert got == expected, (
        f"the right side view of {values} should be {expected}, got {got}. You see the LAST node of every "
        "level; if the right child is missing, a node from the left shows through.")


def test_left_branch_deeper_than_the_right_branch():
    got = right_side_view(build([1, 2, 3, 4, None, None, None, 5]))
    assert got == [1, 3, 4, 5], (
        f"expected [1, 3, 4, 5], got {got}. Below the right branch ends, the left branch is what you see at depth 2 and 3: "
        "do not stop when the rightmost path ends.")


def test_random_trees_against_the_last_of_each_level():
    rng = random.Random(19)
    for _ in range(200):
        t = random_tree(rng, rng.randint(0, 40))
        want = [lv[-1] for lv in levels_of(t)]
        got = right_side_view(t)
        assert got == want, f"the right side view of {to_level(t)} should be {want}, got {got}."
