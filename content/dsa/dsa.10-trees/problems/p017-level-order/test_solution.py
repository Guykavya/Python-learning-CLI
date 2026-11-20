import random
from collections import deque

import pytest

from solution import TreeNode, level_order


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
    assert level_order(None) == [], "An empty tree has no levels: return [] (not [[]] and not [None])."


def test_single_node():
    assert level_order(build([5])) == [[5]], "A single node is one level with one value: [[5]]."


@pytest.mark.parametrize("values, expected", [
    ([3, 9, 20, None, None, 15, 7], [[3], [9, 20], [15, 7]]),
    ([4, 2, 6, 1, 3, 5, 7], [[4], [2, 6], [1, 3, 5, 7]]),
    ([1, None, 2, 3], [[1], [2], [3]]),
    ([1, 2, 3, 4, None, None, 5], [[1], [2, 3], [4, 5]]),
    ([1, 2, None, 3, None, 4], [[1], [2], [3], [4]]),
])
def test_examples(values, expected):
    got = level_order(build(values))
    assert got == expected, (
        f"level order of {values} should be {expected}, got {got}. Each inner list is one depth, "
        "left to right: read len(queue) before the inner loop.")


def test_a_node_without_a_left_child_keeps_the_order():
    got = level_order(build([1, 2, 3, None, 4, 5]))
    assert got == [[1], [2, 3], [4, 5]], f"expected [[1], [2, 3], [4, 5]], got {got}. Append the left child before the right child."


def test_random_trees_against_the_levels_walk():
    rng = random.Random(17)
    for _ in range(200):
        t = random_tree(rng, rng.randint(0, 40))
        want = levels_of(t)
        got = level_order(t)
        assert got == want, f"level order of {to_level(t)} should be {want}, got {got}."


def test_the_tree_is_unchanged():
    t = build([3, 9, 20, None, None, 15, 7])
    level_order(t)
    assert to_level(t) == [3, 9, 20, None, None, 15, 7], "level_order must only read the tree, not change it."
