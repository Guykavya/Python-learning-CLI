import random
from collections import deque

import pytest

from solution import TreeNode, build_from_pre_in


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


def distinct_tree(rng, n):
    """A random tree shape with n nodes and distinct values (so traversals determine the tree)."""
    t = random_tree(rng, n)
    for node, v in zip(nodes(t), rng.sample(range(500), n)):
        node.val = v
    return t


def test_the_chapter_example():
    t = build_from_pre_in([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])
    assert to_level(t) == [3, 9, 20, None, None, 15, 7], (
        f"preorder [3, 9, 20, 15, 7] and inorder [9, 3, 15, 20, 7] give [3, 9, 20, None, None, 15, 7], got {to_level(t)}.")


def test_empty_and_single():
    assert build_from_pre_in([], []) is None, "two empty lists give the empty tree: None."
    t = build_from_pre_in([7], [7])
    assert t is not None and t.val == 7 and t.left is None and t.right is None, "one value: a single node."


def test_the_same_values_in_two_shapes():
    assert to_level(build_from_pre_in([1, 2], [2, 1])) == [1, 2], "inorder [2, 1]: 2 is to the LEFT of 1."
    assert to_level(build_from_pre_in([1, 2], [1, 2])) == [1, None, 2], "inorder [1, 2]: 2 is to the RIGHT of 1."
    assert to_level(build_from_pre_in([1, 2, 3], [3, 2, 1])) == [1, 2, None, 3], "a left chain."
    assert to_level(build_from_pre_in([1, 2, 3], [1, 2, 3])) == [1, None, 2, None, 3], "a right chain."


def test_the_input_lists_are_not_changed():
    pre, ino = [3, 9, 20, 15, 7], [9, 3, 15, 20, 7]
    pre0, ino0 = list(pre), list(ino)
    build_from_pre_in(pre, ino)
    assert pre == pre0 and ino == ino0, (
        "you changed one of the input lists (maybe with pop(0)). Walk the preorder with an index or an iterator instead.")


def test_random_trees_rebuilt_and_checked_by_walking_again():
    rng = random.Random(50)
    for _ in range(300):
        original = distinct_tree(rng, rng.randint(0, 20))
        pre, ino = reference_order(original, "pre"), reference_order(original, "in")
        got = build_from_pre_in(list(pre), list(ino))
        assert reference_order(got, "pre") == pre and reference_order(got, "in") == ino, (
            f"the tree you built has another preorder or inorder than the lists you were given "
            f"(preorder {pre}, inorder {ino}). Left subtree first, and split the inorder list at the root.")
        assert to_level(got) == to_level(original), (
            f"for preorder {pre} and inorder {ino} the tree should be {to_level(original)}, got {to_level(got)}.")


def test_long_chains():
    n = 400
    pre = list(range(1, n + 1))
    t = build_from_pre_in(pre, list(reversed(pre)))      # inorder reversed: every node is a LEFT child
    assert reference_order(t, "pre") == pre and reference_order(t, "in") == list(reversed(pre)), "a left chain of 400 nodes."
    t = build_from_pre_in(pre, list(pre))                # inorder equal: every node is a RIGHT child
    assert reference_order(t, "pre") == pre and reference_order(t, "in") == pre, "a right chain of 400 nodes."
