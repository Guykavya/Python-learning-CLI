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


class Counting(TreeNode):
    """A TreeNode that counts how often its left and right pointers are READ (assigning is free)."""
    reads = 0

    def __init__(self, val=0, left=None, right=None):
        self._left = None
        self._right = None
        super().__init__(val, left, right)

    @property
    def left(self):
        Counting.reads += 1
        return self._left

    @left.setter
    def left(self, node):
        self._left = node

    @property
    def right(self):
        Counting.reads += 1
        return self._right

    @right.setter
    def right(self, node):
        self._right = node


def adjacency(root):
    """The tree as an undirected graph: {node: [neighbours]} (the brute force of chapter section 7)."""
    adj = {}
    for node in nodes(root):
        adj.setdefault(node, [])
        for child in (node.left, node.right):
            if child is not None:
                adj[node].append(child)
                adj.setdefault(child, []).append(node)
    return adj


def bfs_distances(adj, start):
    """Edge distance from start to every node it can reach."""
    dist, queue = {start: 0}, deque([start])
    while queue:
        node = queue.popleft()
        for nxt in adj[node]:
            if nxt not in dist:
                dist[nxt] = dist[node] + 1
                queue.append(nxt)
    return dist


def brute_diameter(root):
    """Brute force: a breadth-first search from every node of the undirected tree."""
    adj = adjacency(root)
    return max((max(bfs_distances(adj, start).values()) for start in adj), default=0)


def test_empty_and_single_node():
    assert diameter(None) == 0, "An empty tree has diameter 0."
    assert diameter(build([1])) == 0, "A single node has diameter 0 edges."


@pytest.mark.parametrize("values, expected", [
    ([3, 9, 20, None, None, 15, 7], 3),
    ([4, 2, 6, 1, 3, 5, 7], 4),
    ([1, 2], 1),
    ([1, 2, 3, 4, 5], 3),
    ([1, None, 2, None, 3, None, 4], 3),
])
def test_examples_that_pass_through_the_root(values, expected):
    got = diameter(build(values))
    assert got == expected, f"diameter({values}) should be {expected} edges, got {got}."


def test_the_longest_path_does_not_pass_through_the_root():
    values = [1, 2, 7, 3, 4, None, None, 5, None, None, 8, 6, None, None, 9]
    got = diameter(build(values))
    assert got == 6, (
        f"The longest path is 6 - 5 - 3 - 2 - 4 - 8 - 9: 6 edges. Your answer {got} measures only the paths through the ROOT "
        "(height(left) + height(right)). The longest path has a highest node that can be anywhere: compute "
        "left + right at every node and keep the maximum.")


def test_a_deep_arm_on_one_side_only():
    # the root has only a left child; the longest path bends at a node two levels down
    values = [1, 2, None, 3, 4, 5, None, None, 8, 6, None, None, 9]
    t = build(values)
    want = brute_diameter(t)
    got = diameter(t)
    assert want == 6, "test data check: the longest path is 6 - 5 - 3 - 2 - 4 - 8 - 9."
    assert got == want, (
        f"the tree {values}: the diameter is {want} edges, got {got}. "
        "The longest path bends at the node 2, not at the root: compute left + right at every node.")


def test_random_trees_against_the_brute_force():
    rng = random.Random(33)
    for _ in range(400):
        t = random_tree(rng, rng.randint(0, 16))
        want = brute_diameter(t)
        got = diameter(t)
        assert got == want, f"the tree {to_level(t)}: the diameter is {want} edges, got {got}."


def test_it_is_one_pass_not_a_height_call_at_every_node():
    n = 1023                                          # a perfect tree with 10 levels
    t = build(list(range(1, n + 1)), make=Counting)
    Counting.reads = 0
    got = diameter(t)
    reads = Counting.reads
    assert got == 18, f"a perfect tree with 10 levels has diameter 18 edges (leaf to leaf through the root), got {got}."
    assert reads <= 8 * n, (
        f"your function read {reads:,} child pointers on a tree of {n:,} nodes; one pass needs only about {2 * n:,}. "
        "Calling height at every node walks the same subtrees again and again. Return the height from the same "
        "recursive call that records the best path.")
