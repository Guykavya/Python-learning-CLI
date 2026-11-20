import random
from collections import deque

import pytest

from solution import TreeNode, root_to_leaf_paths


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


def brute_paths(root):
    """The test's own paths: an explicit stack of (node, text), pushed so that the left child comes out first."""
    out, stack = [], ([(root, str(root.val))] if root is not None else [])
    while stack:
        node, text = stack.pop()
        if node.left is None and node.right is None:
            out.append(text)
        for child in (node.right, node.left):
            if child is not None:
                stack.append((child, text + "->" + str(child.val)))
    return out


def test_empty_tree():
    assert root_to_leaf_paths(None) == [], "An empty tree has no paths: []."


def test_single_node():
    assert root_to_leaf_paths(build([7])) == ["7"], "A single node is a leaf: the one path is the string '7'."


def test_a_node_with_one_child_is_not_a_leaf():
    got = root_to_leaf_paths(build([1, 2]))
    assert got == ["1->2"], f"[1, 2] has one path, '1->2'. The root has a child, so it is not a leaf; got {got}."


@pytest.mark.parametrize("values, expected", [
    ([1, 2, 3, None, 5], ["1->2->5", "1->3"]),
    ([4, 2, 6, 1, 3, 5, 7], ["4->2->1", "4->2->3", "4->6->5", "4->6->7"]),
    ([3, 9, 20, None, None, 15, 7], ["3->9", "3->20->15", "3->20->7"]),
    ([-1, -2], ["-1->-2"]),
    ([1, None, 2, None, 3], ["1->2->3"]),
])
def test_examples(values, expected):
    got = root_to_leaf_paths(build(values))
    assert got == expected, (
        f"the paths of {values} should be {expected}, got {got}. Store a path only at a leaf, left leaves first; "
        "after both children are done, remove the node from the path (backtrack).")


def test_the_path_is_cleaned_up_between_branches():
    got = root_to_leaf_paths(build([1, 2, 3, 4, 5, 6, 7]))
    assert got == ["1->2->4", "1->2->5", "1->3->6", "1->3->7"], (
        f"expected ['1->2->4', '1->2->5', '1->3->6', '1->3->7'], got {got}. "
        "If the second path still contains the 4, you forgot to pop the node when leaving it.")


def test_two_calls_are_independent():
    t = build([1, 2, 3])
    first = root_to_leaf_paths(t)
    second = root_to_leaf_paths(t)
    assert first == second == ["1->2", "1->3"], "calling twice must give the same answer: do not keep the paths in a variable outside the function."


def test_random_trees_against_an_explicit_stack():
    rng = random.Random(29)
    for _ in range(300):
        t = random_tree(rng, rng.randint(0, 30), -9, 99)
        want = brute_paths(t)
        got = root_to_leaf_paths(t)
        assert got == want, f"the paths of {to_level(t)} should be {want}, got {got}."
