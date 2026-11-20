import random
import sys
import tracemalloc
from collections import deque

import pytest

from solution import TreeNode, morris_inorder


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


def right_chain(n):
    """1 -> 2 -> ... -> n, every node has only a right child. Built with a loop."""
    root = None
    for v in range(n, 0, -1):
        root = TreeNode(v, None, root)
    return root


def left_chain(n):
    """1 -> 2 -> ... -> n, every node has only a left child. Built with a loop."""
    root = None
    for v in range(n, 0, -1):
        root = TreeNode(v, root, None)
    return root


def zigzag_chain(n):
    """1, 2, ..., n where each next node is a left child, then a right child, then a left child, ..."""
    made = [TreeNode(v) for v in range(1, n + 1)]
    for i in range(n - 1):
        if i % 2 == 0:
            made[i].left = made[i + 1]
        else:
            made[i].right = made[i + 1]
    return made[0]


def deep_call(f, *args):
    """Call f; turn a RecursionError into a message that says what to do."""
    try:
        return f(*args)
    except RecursionError:
        raise AssertionError(
            "RecursionError: this tree is thousands of nodes deep and a recursive function runs out of stack. "
            "Use an iterative version (an explicit stack) or raise the limit knowingly.") from None


def reference_order(root, order):
    """The test's own traversal (an explicit stack of (node, done) pairs, the chapter's one template)."""
    out, stack = [], [(root, False)]
    while stack:
        node, done = stack.pop()
        if node is None:
            continue
        if done:
            out.append(node.val)
        elif order == "pre":
            stack += [(node.right, False), (node.left, False), (node, True)]
        elif order == "in":
            stack += [(node.right, False), (node, True), (node.left, False)]
        else:
            stack += [(node, True), (node.right, False), (node.left, False)]
    return out


def snapshot(root):
    """Every node with the exact objects it points to (identity, not only values)."""
    return [(node, node.left, node.right) for node in nodes(root)]


def check_restored(root, snap, what):
    try:
        shape = to_level(root)
    except AssertionError:
        raise AssertionError(
            f"{what}: afterwards the tree contains a cycle. A thread (a right pointer to an ancestor) was "
            "not removed: set pred.right = None when you see pred.right is cur.") from None
    for node, left, right in snap:
        assert node.left is left, f"{what}: the left pointer of the node {node.val!r} was changed and not restored."
        assert node.right is right, (
            f"{what}: the right pointer of the node {node.val!r} was changed and not restored: "
            "remove every thread (pred.right = None) before you leave.")
    return shape


def test_empty_tree():
    assert morris_inorder(None) == [], "An empty tree has no values: []."


@pytest.mark.parametrize("values, expected", [
    ([7], [7]),
    ([2, 1, 3], [1, 2, 3]),
    ([4, 2, 6, 1, 3, 5, 7], [1, 2, 3, 4, 5, 6, 7]),
    ([3, 9, 20, None, None, 15, 7], [9, 3, 15, 20, 7]),
    ([1, None, 2, 3], [1, 3, 2]),
    ([1, 2, 3, 4, 5], [4, 2, 5, 1, 3]),
])
def test_examples_and_the_tree_is_restored(values, expected):
    t = build(values)
    before, snap = to_level(t), snapshot(t)
    got = morris_inorder(t)
    assert got == expected, f"inorder of {values} should be {expected}, got {got}."
    after = check_restored(t, snap, f"morris_inorder({values})")
    assert after == before, f"the tree changed from {before} to {after}: restore every pointer you changed."


def test_random_trees_values_and_shape():
    rng = random.Random(24)
    for _ in range(300):
        t = random_tree(rng, rng.randint(0, 30))
        before, snap = to_level(t), snapshot(t)
        got = morris_inorder(t)
        want = reference_order(t, "in")
        assert got == want, f"inorder of {before} should be {short(want, 30)}, got {short(got, 30)}."
        check_restored(t, snap, f"morris_inorder on {before}")


@pytest.mark.parametrize("make", [left_chain, right_chain, zigzag_chain])
def test_chains_of_5000_nodes_need_no_recursion(make):
    t = make(5000)
    want = reference_order(t, "in")
    got = morris_inorder(t)
    assert got == want, f"inorder of a chain of 5000 nodes is wrong; you returned {short(got)}."


def test_extra_memory_is_constant():
    n = 30000
    t = left_chain(n)                                   # a stack would hold all 30,000 nodes here
    tracemalloc.start()
    try:
        out = morris_inorder(t)
        peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    assert out == list(range(n, 0, -1)), "wrong inorder on a left chain of 30,000 nodes."
    limit = 1.2 * sys.getsizeof(out) + 8000
    assert peak <= limit, (
        f"your function used about {peak // 1024} KiB at its peak; the output list alone needs about "
        f"{sys.getsizeof(out) // 1024} KiB. A stack (or any other collection of nodes) adds one slot for every waiting node. "
        "The Morris walk uses no memory besides a few variables and the output list.")
