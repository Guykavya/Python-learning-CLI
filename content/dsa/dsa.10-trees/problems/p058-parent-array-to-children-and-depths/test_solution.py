import random
from collections import deque

import pytest

from solution import TreeNode, children_and_depths


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


def brute(parent):
    n = len(parent)
    children = [[i for i in range(n) if parent[i] == p] for p in range(n)]
    depth = []
    for i in range(n):
        steps, cur = 0, i
        while parent[cur] != -1:
            cur = parent[cur]
            steps += 1
        depth.append(steps)
    return children, depth


def random_parent_array(rng, n):
    """A random tree with n nodes, with random numbers (a parent can have a larger number than its child)."""
    labels = list(range(n))
    rng.shuffle(labels)
    parent = [-1] * n
    for k in range(1, n):
        parent[labels[k]] = labels[rng.randrange(k)]
    return parent


def test_the_chapter_example():
    children, depth = children_and_depths([-1, 0, 0, 1, 1, 2])
    assert children == [[1, 2], [3, 4], [5], [], [], []], f"children should be [[1, 2], [3, 4], [5], [], [], []], got {children}."
    assert depth == [0, 1, 1, 2, 2, 2], f"depths should be [0, 1, 1, 2, 2, 2], got {depth}."


def test_a_single_node():
    got = children_and_depths([-1])
    assert got == ([[]], [0]), f"one node: the pair ([[]], [0]) is expected, got {got}."


@pytest.mark.parametrize("parent, children, depth", [
    ([1, -1], [[], [0]], [1, 0]),
    ([2, 2, -1], [[], [], [0, 1]], [1, 1, 0]),
    ([3, 0, 1, -1], [[1], [2], [], [0]], [1, 2, 3, 0]),
    ([-1, 0, 0, 0], [[1, 2, 3], [], [], []], [0, 1, 1, 1]),
    ([2, 0, -1, 2], [[1], [], [0, 3], []], [1, 2, 0, 1]),
])
def test_the_parent_comes_after_the_child_in_the_array(parent, children, depth):
    got = children_and_depths(parent)
    assert got == (children, depth), (
        f"parent array {parent}: expected {(children, depth)}, got {got}. The root is the node with parent -1 "
        "(not always node 0), and a node's parent can have a LARGER number: do not compute depths in array order.")


def test_random_trees_against_climbing_the_parents():
    rng = random.Random(58)
    for _ in range(400):
        parent = random_parent_array(rng, rng.randint(1, 40))
        want = brute(parent)
        got = children_and_depths(parent)
        assert got == want, f"parent array {parent}: expected {want}, got {got}."


def test_a_path_of_5000_nodes_with_the_root_first_and_last():
    n = 5000
    forward = [-1] + list(range(n - 1))                      # parent[i] = i - 1: the root is node 0
    children, depth = children_and_depths(forward)
    assert depth == list(range(n)), "a path with the root first: the depth of node i is i."
    assert children[0] == [1] and children[n - 1] == [], "node 0 has the child 1 and the last node is a leaf."
    backward = list(range(1, n)) + [-1]                      # parent[i] = i + 1: the root is node n - 1
    children, depth = children_and_depths(backward)
    assert depth == list(range(n - 1, -1, -1)), (
        "a path with the root last: the depth of node i is n - 1 - i. "
        "(No recursion: a path of 5,000 nodes is deeper than the recursion limit.)")


def test_a_star():
    n = 5000
    parent = [-1] + [0] * (n - 1)
    children, depth = children_and_depths(parent)
    assert children[0] == list(range(1, n)), "the root has all the other nodes as children, in increasing order."
    assert depth == [0] + [1] * (n - 1), "every other node is at depth 1."
