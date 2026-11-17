import random
from collections import deque

import pytest

from solution import TreeNode, lca


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


def parent_ids(root):
    """{id(node): parent node or None} for every node (a plain loop; the test's own helper)."""
    parent = {id(root): None}
    for node in nodes(root):
        for child in (node.left, node.right):
            if child is not None:
                parent[id(child)] = node
    return parent


def brute_lca(root, p, q):
    """The lowest node on the path root -> q that is also on the path root -> p (parent links, no recursion)."""
    parent = parent_ids(root)
    above_p, cur = set(), p
    while cur is not None:
        above_p.add(id(cur))
        cur = parent[id(cur)]
    cur = q
    while id(cur) not in above_p:
        cur = parent[id(cur)]
    return cur


def by_value(root):
    """{value: node} for a tree with distinct values."""
    return {n.val: n for n in nodes(root)}


def test_the_chapter_tree():
    t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
    n = by_value(t)
    cases = [(5, 1, 3), (5, 4, 5), (6, 4, 5), (7, 8, 3), (7, 4, 2), (6, 8, 3), (0, 8, 1), (3, 7, 3), (4, 5, 5)]
    for a, b, want in cases:
        got = lca(t, n[a], n[b])
        assert got is n[want], (
            f"the LCA of {a} and {b} should be the node {want}, got "
            f"{'None' if got is None else got.val}. Return the node when both sides found one of p and q.")


def test_a_node_is_its_own_ancestor():
    t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
    n = by_value(t)
    for v in (3, 5, 7, 8):
        assert lca(t, n[v], n[v]) is n[v], f"the LCA of the node {v} with itself is that node."
    one = build([9])
    assert lca(one, one, one) is one, "a single node tree: the LCA of the node with itself is the node."
    assert lca(t, n[3], n[7]) is n[3], "the root is an ancestor of every node, so the LCA of the root and 7 is the root."
    assert lca(t, n[7], n[3]) is n[3], "the order of p and q must not matter."


def test_equal_values_must_be_compared_as_nodes():
    t = build([1, 1, 1, 1, 1, 1, 1])
    by_position = {}
    queue = deque([t])
    while queue:
        node = queue.popleft()
        by_position[len(by_position)] = node
        for child in (node.left, node.right):
            if child is not None:
                queue.append(child)
    p, q = by_position[3], by_position[4]          # the two children of the left child of the root
    got = lca(t, p, q)
    assert got is by_position[1], (
        "every value is 1, and p, q are the two children of the left child of the root, so the LCA is that left "
        "child. If you got another node you compared values: compare the nodes with `is`.")


def test_a_deep_chain():
    t = left_chain(300)
    chain = nodes(t)                                 # a chain: the order is root first
    assert lca(t, chain[299], chain[100]) is chain[100], "the node 100 is an ancestor of the node 299 on a chain."
    assert lca(t, chain[0], chain[299]) is chain[0], "the root is the LCA of the root and the last node."
    z = zigzag_chain(300)
    zc = nodes(z)
    assert lca(z, zc[250], zc[299]) is zc[250], "on a zigzag chain the earlier node is the ancestor."


def test_random_trees_against_the_parent_map_brute_force():
    rng = random.Random(47)
    for _ in range(500):
        t = random_tree(rng, rng.randint(1, 20))     # values 0..9: many repeats
        all_ = nodes(t)
        p, q = rng.choice(all_), rng.choice(all_)
        want = brute_lca(t, p, q)
        got = lca(t, p, q)
        assert got is want, (
            f"tree {to_level(t)}: for two nodes with values {p.val} and {q.val} the LCA has value "
            f"{want.val} but your function returned {'None' if got is None else got.val}.")
