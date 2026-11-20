import random
from collections import deque

import pytest

from solution import TreeNode, sum_numbers


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


def brute_sum(root):
    """The test's own sum: spell every path as a string and convert it (an explicit stack)."""
    total, stack = 0, ([(root, str(root.val))] if root is not None else [])
    while stack:
        node, text = stack.pop()
        if node.left is None and node.right is None:
            total += int(text)
        for child in (node.left, node.right):
            if child is not None:
                stack.append((child, text + str(child.val)))
    return total


def test_empty_tree():
    assert sum_numbers(None) == 0, "An empty tree has no paths: the sum is 0."


def test_single_node():
    assert sum_numbers(build([7])) == 7, "A single node is a leaf: the number is its digit."
    assert sum_numbers(build([0])) == 0, "The single digit 0 is the number 0."


@pytest.mark.parametrize("values, expected", [
    ([1, 2, 3], 25),
    ([4, 9, 0, 5, 1], 1026),
    ([1, 2], 12),
    ([1, None, 2, None, 3], 123),
    ([0, 1], 1),
    ([9, 9, 9, 9, 9, 9, 9], 3996),
])
def test_examples(values, expected):
    got = sum_numbers(build(values))
    assert got == expected, (
        f"the numbers of the paths of {values} add up to {expected}, got {got}. Multiply the number so far by 10 "
        "and add the digit; add the number to the answer only at a leaf.")


def test_a_node_with_one_child_counts_only_the_full_path():
    got = sum_numbers(build([1, 2]))
    assert got == 12, f"[1, 2] has the single path 1 -> 2, the number 12; got {got}. The root is not a leaf, so '1' alone is not counted."


def test_random_trees_against_strings():
    rng = random.Random(30)
    for _ in range(300):
        t = random_tree(rng, rng.randint(0, 30), 0, 9)
        want = brute_sum(t)
        got = sum_numbers(t)
        assert got == want, f"the numbers of the paths of {to_level(t)} add up to {want}, got {got}."
