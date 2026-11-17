import random
from collections import deque

import pytest

from solution import TreeNode, distance


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


def brute_distance(root, p, q):
    adj = adjacency(root)
    return bfs_distances(adj, p)[q]


def test_the_chapter_tree():
    t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
    n = {node.val: node for node in nodes(t)}
    cases = [(7, 8, 5), (6, 4, 3), (5, 7, 2), (5, 5, 0), (3, 7, 3), (3, 3, 0), (0, 8, 2), (6, 7, 3)]
    for a, b, want in cases:
        got = distance(t, n[a], n[b])
        assert got == want, (
            f"the distance between {a} and {b} should be {want} edges, got {got}. "
            "depth(p) + depth(q) - 2 * depth(lca); a node to itself is 0.")
        assert distance(t, n[b], n[a]) == want, f"the order of the two nodes must not matter ({b}, {a})."


def test_single_node():
    t = build([4])
    assert distance(t, t, t) == 0, "a node to itself is 0 edges."


def test_one_node_is_an_ancestor_of_the_other():
    t = build([1, 2, 3, 4, 5, 6, 7])
    root = t
    deepest = t.left.left
    assert distance(t, root, deepest) == 2, "the root and a grandchild: 2 edges."
    assert distance(t, deepest, root) == 2, "the order must not matter."
    assert distance(t, t.left, deepest) == 1, "a node and its child: 1 edge."


def test_repeated_values_compare_nodes_not_values():
    t = build([5, 5, 5, 5, 5, 5, 5])
    leaf_a, leaf_b = t.left.left, t.right.right
    assert distance(t, leaf_a, leaf_b) == 4, (
        "all values are 5; the two leaves are on different sides of the root: 2 + 2 = 4 edges. "
        "If you found another number, you looked nodes up by value.")


def test_a_long_chain():
    t = left_chain(300)
    chain = nodes(t)
    assert distance(t, chain[0], chain[299]) == 299, "the two ends of a chain of 300 nodes are 299 edges apart."
    assert distance(t, chain[100], chain[250]) == 150, "positions 100 and 250 on a chain: 150 edges."


def test_random_trees_against_a_breadth_first_search():
    rng = random.Random(49)
    for _ in range(500):
        t = random_tree(rng, rng.randint(1, 25))
        all_ = nodes(t)
        p, q = rng.choice(all_), rng.choice(all_)
        want = brute_distance(t, p, q)
        got = distance(t, p, q)
        assert got == want, f"tree {to_level(t)}: the distance between two nodes (values {p.val} and {q.val}) is {want}, got {got}."
