import random
from collections import deque

import pytest

from solution import TreeNode, max_path_sum


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


def brute_best(root):
    """Brute force: every start node, every walk in the undirected tree that never goes back."""
    adj = adjacency(root)
    best = float("-inf")
    for start in adj:
        todo = [(start, None, start.val)]
        while todo:
            node, came_from, total = todo.pop()
            best = max(best, total)
            for nxt in adj[node]:
                if nxt is not came_from:
                    todo.append((nxt, node, total + nxt.val))
    return best


@pytest.mark.parametrize("values, expected", [
    ([1, 2, 3], 6),
    ([-10, 9, 20, None, None, 15, 7], 42),
    ([-3], -3),
    ([2, -1], 2),
    ([-2, -1], -1),
    ([-1, -2, -3], -1),
    ([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1], 48),
    ([1, -2, 3], 4),
    ([1, 2, None, 3, None, 4], 10),
])
def test_examples(values, expected):
    got = max_path_sum(build(values))
    assert got == expected, (
        f"max_path_sum({values}) should be {expected}, got {got}. Return ONE branch to the parent, record the bent "
        "path in a separate variable, and drop branches with a negative gain.")


def test_all_negative_values_return_the_largest_single_value():
    for values, expected in (([-3], -3), ([-7, -2, -9], -2), ([-5, -4, -8, -9, -1], -1)):
        got = max_path_sum(build(values))
        assert got == expected, (
            f"{values}: every value is negative, so the best path is the single largest node, {expected}; got {got}. "
            "Start best at float('-inf'), not 0, and never answer 0 when the tree is not empty.")


def test_the_best_path_does_not_have_to_use_the_root():
    # the root is -100; the best path 5 - 6 - 7 lies completely inside the left subtree
    got = max_path_sum(build([-100, 6, -50, 5, 7]))
    assert got == 18, (
        f"5 - 6 - 7 adds up to 18 and does not touch the root, got {got}. Record the bent path at EVERY node, "
        "not only at the root.")


def test_a_parent_can_use_only_one_branch_of_its_child():
    # at node 3 the best bent path is 4 + 3 + 5 = 12, but the parent 1 can only take 3 + 5 = 8 or 3 + 4 = 7
    got = max_path_sum(build([1, 3, None, 4, 5]))
    assert got == 12, f"the best path is 4 - 3 - 5 = 12, got {got}."
    got2 = max_path_sum(build([-20, 3, None, 4, 5]))
    assert got2 == 12, (
        f"with a root of -20 the answer is still 4 - 3 - 5 = 12, got {got2}. If you got more, you returned the bent "
        "path to the parent: return node.val + max(left, right), not node.val + left + right.")


def test_random_trees_against_the_brute_force():
    rng = random.Random(32)
    for _ in range(400):
        t = random_tree(rng, rng.randint(1, 14), -6, 6)
        want = brute_best(t)
        got = max_path_sum(t)
        assert got == want, f"the tree {to_level(t)}: the best path sum is {want}, got {got}."
    for _ in range(60):
        t = random_tree(rng, rng.randint(20, 45), -9, 5)
        want = brute_best(t)
        got = max_path_sum(t)
        assert got == want, f"the tree {to_level(t)}: the best path sum is {want}, got {got}."


def test_a_long_chain_with_mixed_signs():
    n = 400
    t = left_chain(n)
    node, sign = t, 1
    while node is not None:
        node.val = sign * (node.val % 7 + 1)
        sign = -sign
        node = node.left
    want = brute_best(t)
    got = max_path_sum(t)
    assert got == want, f"a chain of {n} nodes with alternating signs: the best path sum is {want}, got {got}."
