import random
from collections import deque

import pytest

from solution import TreeNode, count_good_nodes


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


def brute_good(root):
    """The test's own count: for every node, look at all its ancestors with a parent map."""
    parent = {}
    for node in nodes(root):
        for child in (node.left, node.right):
            if child is not None:
                parent[id(child)] = node
    count = 0
    for node in nodes(root):
        up, good = parent.get(id(node)), True
        while up is not None:
            if up.val > node.val:
                good = False
            up = parent.get(id(up))
        count += good
    return count


def test_empty_tree():
    assert count_good_nodes(None) == 0, "An empty tree has no nodes, so no good nodes."


def test_single_node_is_good_even_when_negative():
    assert count_good_nodes(build([-7])) == 1, "The root is always good (it has no ancestors), also when it is negative. Do not start the maximum at 0."


@pytest.mark.parametrize("values, expected", [
    ([3, 1, 4, 3, None, 1, 5], 4),
    ([3, 3, None, 4, 2], 3),
    ([-1, -5, -3], 1),
    ([-5, -1, -3], 3),
    ([2, 2, 2], 3),
    ([1, 2, 3], 3),
    ([9, 1, 2], 1),
])
def test_examples(values, expected):
    got = count_good_nodes(build(values))
    assert got == expected, (
        f"{values} has {expected} good nodes, got {got}. A node is good when no ancestor is LARGER "
        "(equal is fine); compare with the largest ancestor, not only the parent, and update it going down.")


def test_compare_with_the_grandparent_not_only_the_parent():
    got = count_good_nodes(build([5, 1, None, 3]))        # 5 -> 1 -> 3: the 3 is larger than its parent, but not than 5
    assert got == 1, f"5 -> 1 -> 3: the 3 is larger than its parent 1 but smaller than the ancestor 5, so only the root is good. Got {got}."


def test_chains():
    assert count_good_nodes(right_chain(400)) == 400, "In 1 -> 2 -> ... -> 400 every node is larger than all its ancestors: all 400 are good."
    down = None
    for v in range(1, 401):
        down = TreeNode(v, down, None)                       # 400 -> 399 -> ... -> 1 on the left
    assert count_good_nodes(down) == 1, "In 400 -> 399 -> ... -> 1 only the root is good."


def test_random_trees_with_negative_values():
    rng = random.Random(20)
    for _ in range(200):
        t = random_tree(rng, rng.randint(0, 30), -6, 6)
        want = brute_good(t)
        got = count_good_nodes(t)
        assert got == want, f"the tree {to_level(t)} has {want} good nodes, got {got}."
