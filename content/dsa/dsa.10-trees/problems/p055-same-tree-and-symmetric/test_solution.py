import random
from collections import deque

import pytest

from solution import TreeNode, same_tree, is_symmetric


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


def mirror_copy(root):
    """A mirror image of the tree made of NEW nodes (the test's own helper, no recursion)."""
    if root is None:
        return None
    copies = {id(n): TreeNode(n.val) for n in nodes(root)}
    for n in nodes(root):
        c = copies[id(n)]
        c.left = copies[id(n.right)] if n.right is not None else None
        c.right = copies[id(n.left)] if n.left is not None else None
    return copies[id(root)]


def test_same_tree_empty_cases():
    assert same_tree(None, None) is True, "two empty trees are the same."
    assert same_tree(None, build([1])) is False, "an empty tree and a single node are different."
    assert same_tree(build([1]), None) is False, "a single node and an empty tree are different."


@pytest.mark.parametrize("a, b, expected", [
    ([1, 2, 3], [1, 2, 3], True),
    ([1], [1], True),
    ([1], [2], False),
    ([1, 2, 3], [1, 3, 2], False),
    ([1, 2], [1, None, 2], False),
    ([1, 2, 3], [1, 2], False),
    ([1, 2, None, 3], [1, 2, None, 4], False),
    ([4, 2, 6, 1, 3, 5, 7], [4, 2, 6, 1, 3, 5, 7], True),
])
def test_same_tree_examples(a, b, expected):
    got = same_tree(build(a), build(b))
    assert got is expected, (
        f"same_tree({a}, {b}) should be {expected}, got {got}. Compare the shape as well as the values: "
        "an empty left subtree is not the same as a non-empty one.")


def test_same_values_and_traversals_but_a_different_shape():
    a = build([2, 1])               # inorder [1, 2]
    b = build([1, None, 2])         # inorder [1, 2]
    assert same_tree(a, b) is False, (
        "[2, 1] and [1, None, 2] have the same inorder list [1, 2] but they are different trees. "
        "Compare node by node, not a traversal list.")


def test_same_tree_random_pairs_against_level_order_lists():
    rng = random.Random(55)
    same_seen = 0
    for _ in range(500):
        a = random_tree(rng, rng.randint(0, 6), 0, 2)
        b = random_tree(rng, rng.randint(0, 6), 0, 2)
        for other in (b, build(to_level(a))):
            want = to_level(a) == to_level(other)
            same_seen += want
            got = same_tree(a, other)
            assert got is want, f"same_tree({to_level(a)}, {to_level(other)}) should be {want}, got {got}."
    assert same_seen >= 500, "test data check: the copies must be recognised as the same."


@pytest.mark.parametrize("values, expected", [
    ([], True),
    ([1], True),
    ([1, 2, 2], True),
    ([1, 2, 3], False),
    ([1, 2], False),
    ([1, None, 2], False),
    ([1, 2, 2, 3, 4, 4, 3], True),
    ([1, 2, 2, None, 3, None, 3], False),
    ([1, 2, 2, 3, None, None, 3], True),
    ([1, 2, 2, None, 3, 3], True),
])
def test_symmetric_examples(values, expected):
    got = is_symmetric(build(values))
    assert got is expected, (
        f"is_symmetric({values}) should be {expected}, got {got}. "
        "A mirror compares the LEFT child of one side with the RIGHT child of the other side.")


def test_symmetric_random_trees_against_a_mirror_copy():
    rng = random.Random(56)
    symmetric_seen = 0
    for i in range(500):
        half = random_tree(rng, rng.randint(0, 6), 0, 2)
        t = TreeNode(rng.randint(0, 2), half, mirror_copy(half))     # a symmetric tree
        if i % 2 == 1:
            all_ = nodes(t)
            rng.choice(all_).val += 1                               # damage it in one place
        if i % 5 == 4:
            t = random_tree(rng, rng.randint(0, 8), 0, 2)
        want = to_level(t) == to_level(mirror_copy(t))
        symmetric_seen += want
        got = is_symmetric(t)
        assert got is want, f"the tree {to_level(t)}: is_symmetric should be {want}, got {got}."
    assert symmetric_seen > 100, "test data check: many of the trees must be symmetric."
