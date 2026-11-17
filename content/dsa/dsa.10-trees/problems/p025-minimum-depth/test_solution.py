import random
from collections import deque

import pytest

from solution import TreeNode, min_depth


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
    assert min_depth(None) == 0, "An empty tree has minimum depth 0."


def test_single_node():
    assert min_depth(build([5])) == 1, "A single node is a leaf at depth 1."


def test_a_node_with_one_child_is_not_a_leaf():
    got = min_depth(build([1, None, 2, None, 3]))
    assert got == 3, (
        f"for 1 -> 2 -> 3 (right chain) the only leaf is 3, so the answer is 3, got {got}. "
        "A missing child is not a leaf: do not let min_depth(None) = 0 win the min.")
    got = min_depth(build([1, 2]))
    assert got == 2, f"[1, 2]: the root has one child, so it is not a leaf; the answer is 2, got {got}."


@pytest.mark.parametrize("values, expected", [
    ([3, 9, 20, None, None, 15, 7], 2),
    ([1, 2, 3, 4, 5], 2),
    ([1, 2, 3, 4, None, None, 5], 3),
    ([2, None, 3, None, 4, None, 5, None, 6], 5),
    ([1, 2, None, 3, None, 4], 4),
    ([1, 2, 3, 4, 5, 6, 7], 3),
])
def test_examples(values, expected):
    got = min_depth(build(values))
    assert got == expected, f"the minimum depth of {values} is {expected}, got {got}."


def test_skewed_tree_of_500_nodes():
    root = None
    for v in range(500):
        root = TreeNode(v, None, root)
    got = min_depth(root)
    assert got == 500, f"a chain of 500 nodes has its only leaf at depth 500, got {got}."


def test_random_trees_against_the_first_level_with_a_leaf():
    rng = random.Random(25)
    for _ in range(300):
        t = random_tree(rng, rng.randint(0, 40))
        if t is None:
            want = 0
        else:
            level, depth, want = [t], 1, None
            while level and want is None:
                if any(n.left is None and n.right is None for n in level):
                    want = depth
                level = [c for n in level for c in (n.left, n.right) if c is not None]
                depth += 1
        got = min_depth(t)
        assert got == want, f"the minimum depth of {to_level(t)} is {want}, got {got}."
