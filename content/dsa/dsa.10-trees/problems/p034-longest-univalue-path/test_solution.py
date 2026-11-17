import random
from collections import deque

import pytest

from solution import TreeNode, longest_univalue_path


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


def brute_univalue(root):
    """Brute force: keep only the edges between equal values, then a BFS from every node."""
    adj = {}
    for node in nodes(root):
        adj.setdefault(node, [])
        for child in (node.left, node.right):
            if child is not None and child.val == node.val:
                adj[node].append(child)
                adj.setdefault(child, []).append(node)
    return max((max(bfs_distances(adj, start).values()) for start in adj), default=0)


def test_empty_and_single_node():
    assert longest_univalue_path(None) == 0, "An empty tree has length 0."
    assert longest_univalue_path(build([7])) == 0, "A single node is a path of 0 edges."


@pytest.mark.parametrize("values, expected", [
    ([5, 4, 5, 1, 1, None, 5], 2),
    ([1, 4, 5, 4, 4, None, 5], 2),
    ([2, 2, 2], 2),
    ([1, 2, None, 1], 0),
    ([1, 1], 1),
    ([1, 2, 2, 2, 2, 2, 2], 2),
    ([4, 4, 4, 4, 4, 4, 4, 4], 5),
    ([1, None, 1, None, 1, None, 2, None, 2], 2),
])
def test_examples(values, expected):
    got = longest_univalue_path(build(values))
    assert got == expected, (
        f"longest_univalue_path({values}) should be {expected} edges, got {got}. A branch continues into a child "
        "only when the child has the SAME value as this node; return one branch, record the bend.")


def test_the_value_two_steps_down_does_not_count_if_the_middle_differs():
    got = longest_univalue_path(build([1, 2, 1, 1]))
    assert got == 1, (
        f"[1, 2, 1, 1]: the node 2 breaks the left side, the right side is 1 - 1 (the 1 below the right child), "
        f"so the answer is 1, got {got}. Compare each child's value with THIS node's value.")


def test_a_path_that_bends_at_the_root_of_a_perfect_tree():
    got = longest_univalue_path(build([3, 3, 3, 3, 3, 3, 3]))
    assert got == 4, (
        f"seven equal nodes in a perfect tree: the longest path goes from a leaf up to the root and down to a leaf "
        f"on the other side, 4 edges; got {got}. Record left_len + right_len at every node.")
    got = longest_univalue_path(build([9, 3, 3, 3, 3, 3, 3]))
    assert got == 2, (
        f"the root 9 separates two groups of three 3s; the best path inside one group is 2 edges, got {got}. "
        "A branch must not continue through a node with a different value.")


def test_random_trees_with_few_values_against_the_brute_force():
    rng = random.Random(34)
    for _ in range(500):
        t = random_tree(rng, rng.randint(0, 16), 0, 2)
        want = brute_univalue(t)
        got = longest_univalue_path(t)
        assert got == want, f"the tree {to_level(t)}: the longest univalue path is {want} edges, got {got}."


def test_a_long_chain_of_equal_values_with_one_break():
    n = 400
    t = left_chain(n)
    for node in nodes(t):
        node.val = 5
    nodes_in_order = nodes(t)
    nodes_in_order[150].val = 6                       # one different value in the middle
    got = longest_univalue_path(t)
    assert got == max(150 - 1, n - 151 - 1), (
        f"a chain of {n} nodes with a single different value at position 151: the longest equal stretch has "
        f"{n - 151} nodes, so {n - 151 - 1} edges; got {got}.")
