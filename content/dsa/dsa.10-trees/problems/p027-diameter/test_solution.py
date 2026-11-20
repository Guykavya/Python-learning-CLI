import random
from collections import deque

import pytest

from solution import TreeNode, diameter


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


def diameter_brute(root):
    """The test's own check: a BFS from every node over the tree seen as an undirected graph."""
    if root is None:
        return 0
    adj = {}
    for node in nodes(root):
        adj.setdefault(id(node), [])
        for child in (node.left, node.right):
            if child is not None:
                adj[id(node)].append(id(child))
                adj.setdefault(id(child), []).append(id(node))
    best = 0
    for start in adj:
        dist, queue = {start: 0}, deque([start])
        while queue:
            cur = queue.popleft()
            for nxt in adj[cur]:
                if nxt not in dist:
                    dist[nxt] = dist[cur] + 1
                    queue.append(nxt)
        best = max(best, max(dist.values()))
    return best


def two_arms_below_a_short_side(k):
    """Root 1 with a single child 3; the node 3 has a left arm and a right arm of k nodes each."""
    arm_left = None
    arm_right = None
    for v in range(k):
        arm_left = TreeNode(10 + v, arm_left, None)
        arm_right = TreeNode(20 + v, None, arm_right)
    return TreeNode(1, None, TreeNode(3, arm_left, arm_right))


def test_empty_and_single():
    assert diameter(None) == 0, "An empty tree has diameter 0."
    assert diameter(build([1])) == 0, "A single node has no edge: diameter 0 (edges, not nodes)."


@pytest.mark.parametrize("values, expected", [
    ([1, 2], 1),
    ([1, 2, 3], 2),
    ([3, 9, 20, None, None, 15, 7], 3),
    ([4, 2, 6, 1, 3, 5, 7], 4),
    ([1, 2, 3, 4, 5], 3),
    ([1, None, 2, None, 3, None, 4, None, 5], 4),
])
def test_examples(values, expected):
    got = diameter(build(values))
    assert got == expected, (
        f"the diameter of {values} is {expected} edges, got {got}. If you are one too high you counted nodes; "
        "if you are too low, the longest path may bend at a node that is not the root.")


def test_longest_path_does_not_pass_through_the_root():
    t = two_arms_below_a_short_side(5)
    got = diameter(t)
    assert got == 10, (
        f"the two arms of 5 nodes below the node 3 give a path of 10 edges that does not touch the root; got {got}. "
        "Record left + right at EVERY node, not only at the root.")


def test_a_chain_of_500_nodes():
    assert diameter(right_chain(500)) == 499, "a chain of 500 nodes has 499 edges."


def test_random_trees_against_a_bfs_from_every_node():
    rng = random.Random(27)
    for _ in range(300):
        t = random_tree(rng, rng.randint(0, 14))
        want = diameter_brute(t)
        got = diameter(t)
        assert got == want, f"the diameter of {to_level(t)} is {want}, got {got}."
