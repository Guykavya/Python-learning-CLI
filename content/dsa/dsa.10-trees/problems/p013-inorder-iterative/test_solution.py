import random
from collections import deque

import pytest

from solution import TreeNode, inorder_iter


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


def test_empty_tree():
    assert inorder_iter(None) == [], "An empty tree has no values: return []."


@pytest.mark.parametrize("values, expected", [
    ([7], [7]),
    ([4, 2, 6, 1, 3, 5, 7], [1, 2, 3, 4, 5, 6, 7]),
    ([3, 9, 20, None, None, 15, 7], [9, 3, 15, 20, 7]),
    ([1, None, 2, 3], [1, 3, 2]),
    ([1, 2, 3, 4, 5], [4, 2, 5, 1, 3]),
    ([1, 2, None, 3], [3, 2, 1]),
])
def test_examples(values, expected):
    got = inorder_iter(build(values))
    assert got == expected, (
        f"inorder of {values} should be {expected}, got {got}. Visit a node only AFTER its left subtree is "
        "finished (when you pop it), and go on with its right child.")


def test_a_tree_that_is_not_a_search_tree():
    rng = random.Random(13)
    t = build(rng.sample(range(100), 15))                 # shuffled values: the order comes from the shape, not the values
    got = inorder_iter(t)
    assert got == reference_order(t, "in"), f"inorder is decided by the shape of the tree, not by the values; got {got}."


def test_random_trees_and_the_tree_is_unchanged():
    rng = random.Random(14)
    for _ in range(200):
        t = random_tree(rng, rng.randint(0, 30))
        before = to_level(t)
        want = reference_order(t, "in")
        got = inorder_iter(t)
        assert got == want, f"inorder of {before} should be {short(want, 30)}, got {short(got, 30)}."
        assert to_level(t) == before, "the traversal must not change the tree."


def test_deep_chains_of_5000_nodes():
    n = 5000
    got = deep_call(inorder_iter, right_chain(n))
    assert got == list(range(1, n + 1)), f"inorder of a right chain 1..5000 is 1, 2, ..., 5000; you returned {short(got)}."
    got = deep_call(inorder_iter, left_chain(n))
    assert got == list(range(n, 0, -1)), f"inorder of a left chain 1..5000 is 5000, ..., 2, 1; you returned {short(got)}."
    t = zigzag_chain(n)
    got = deep_call(inorder_iter, t)
    assert got == reference_order(t, "in"), f"wrong inorder on a zigzag chain of 5000 nodes; you returned {short(got)}."
