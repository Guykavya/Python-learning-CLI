import random
from collections import deque

import pytest

from solution import TreeNode, has_path_sum


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


def leaf_sums(root):
    """The test's own list of the sums of all root-to-leaf paths (an explicit stack)."""
    out, stack = [], ([(root, root.val)] if root is not None else [])
    while stack:
        node, total = stack.pop()
        if node.left is None and node.right is None:
            out.append(total)
        for child in (node.left, node.right):
            if child is not None:
                stack.append((child, total + child.val))
    return out


BIG = [5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1]


def test_empty_tree_has_no_path():
    assert has_path_sum(None, 0) is False, "An empty tree has no path at all, even for target 0."
    assert has_path_sum(None, 5) is False, "An empty tree has no path."


@pytest.mark.parametrize("target, expected", [(22, True), (26, True), (18, True), (27, True), (5, False), (9, False), (28, False), (0, False)])
def test_known_tree(target, expected):
    got = has_path_sum(build(BIG), target)
    assert got is expected, (
        f"the root-to-leaf sums of {BIG} are 27, 22, 26 and 18; target {target} should give {expected}, got {got}.")


def test_the_root_alone_is_not_a_path_when_it_has_a_child():
    assert has_path_sum(build([1, 2]), 1) is False, (
        "[1, 2] and target 1: the root alone sums to 1, but the root has a child, so it is not a leaf. "
        "Compare the sum only at a leaf.")
    assert has_path_sum(build([1, 2]), 3) is True, "[1, 2] and target 3: the path 1 -> 2 ends at the leaf 2."
    assert has_path_sum(build([1, None, 2]), 1) is False, "[1, None, 2]: the root has a right child; the path must go on to 2."


def test_single_node_is_a_leaf():
    assert has_path_sum(build([7]), 7) is True, "A single node is a leaf: the path is just that node."
    assert has_path_sum(build([7]), 8) is False, "A single node of value 7 has the only path sum 7."


def test_negative_values():
    t = build([-2, None, -3])
    assert has_path_sum(t, -5) is True, "-2 -> -3 has the sum -5. Do not give up when the remaining sum becomes negative."
    assert has_path_sum(t, -2) is False, "-2 alone is not a path: the root has a child."
    t = build([10, 5, -3, -8])
    assert has_path_sum(t, 7) is True, "10 -> 5 -> -8 has the sum 7."


def test_random_trees_against_all_leaf_sums():
    rng = random.Random(28)
    for _ in range(300):
        t = random_tree(rng, rng.randint(0, 25), -5, 9)
        sums = set(leaf_sums(t))
        for target in range(-12, 30):
            want = target in sums
            got = has_path_sum(t, target)
            assert got is want, f"the tree {to_level(t)}, target {target}: the leaf sums are {sorted(sums)}, expected {want}, got {got}."
