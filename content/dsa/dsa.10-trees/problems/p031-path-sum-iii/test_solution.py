import random
from collections import deque

import pytest

from solution import TreeNode, path_sum_count


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


def slow_count(root, target):
    """Brute force: start a downward walk at every node."""
    total = 0
    for start in nodes(root):
        stack = [(start, 0)]
        while stack:
            node, before = stack.pop()
            now = before + node.val
            if now == target:
                total += 1
            for child in (node.left, node.right):
                if child is not None:
                    stack.append((child, now))
    return total


def test_empty_and_single_node():
    assert path_sum_count(None, 0) == 0, "An empty tree has no path at all, not even for the target 0."
    assert path_sum_count(build([5]), 5) == 1, "A single node is a path: [5] with target 5 has exactly 1."
    assert path_sum_count(build([5]), 4) == 0, "[5] with target 4: no path adds up to 4."


@pytest.mark.parametrize("values, target, expected", [
    ([10, 5, -3, 3, 2, None, 11, 3, -2, None, 1], 8, 3),
    ([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1], 22, 3),
    ([1, 2, 3], 2, 1),
    ([1, 2, 3], 3, 2),
    ([1, -1, 1], 0, 1),
    ([0, 0, 0], 0, 5),
    ([1, None, 1, None, 1, None, 1], 2, 3),
])
def test_examples(values, target, expected):
    got = path_sum_count(build(values), target)
    assert got == expected, (
        f"path_sum_count({values}, {target}) should be {expected}, got {got}. A path may start at ANY node and end at "
        "any node below it. Check counts = {0: 1} and the order: look up running - target before you record running.")


def test_paths_that_start_at_the_root_are_counted():
    got = path_sum_count(build([3, 1, 2]), 4)
    assert got == 1, (
        f"3 -> 1 starts at the root and adds up to 4, so the answer is 1, got {got}. "
        "Start the dictionary with {0: 1}: the sum 0 happened once, before the root.")


def test_the_left_branch_must_not_leak_into_the_right_branch():
    # both children of the root have the running sum 3; no path has the sum 0
    got = path_sum_count(build([1, 2, 2]), 0)
    assert got == 0, (
        f"[1, 2, 2] with target 0: no path adds up to 0, so the answer is 0, got {got}. The left child and the right "
        "child both have the running sum 3, but they are brothers, not on one path. When you leave a node, take its "
        "running sum back out of the dictionary (counts[running] -= 1).")


def test_zero_target_does_not_count_empty_paths():
    got = path_sum_count(build([5, 3, 4]), 0)
    assert got == 0, (
        f"No node and no downward path adds up to 0 in [5, 3, 4], got {got}. If you record the running sum before "
        "you look up running - target, every node 'finds itself' when target is 0.")


def test_random_trees_with_negative_values_against_the_slow_way():
    rng = random.Random(31)
    for _ in range(300):
        t = random_tree(rng, rng.randint(0, 14), -4, 6)
        target = rng.randint(-4, 8)
        want = slow_count(t, target)
        got = path_sum_count(t, target)
        assert got == want, f"the tree {to_level(t)} with target {target}: expected {want} paths, got {got}."
    for _ in range(60):
        t = random_tree(rng, rng.randint(20, 45), -3, 3)
        target = rng.randint(-3, 5)
        want = slow_count(t, target)
        got = path_sum_count(t, target)
        assert got == want, f"the tree {to_level(t)} with target {target}: expected {want} paths, got {got}."


def test_two_calls_do_not_share_state():
    t = build([10, 5, -3, 3, 2, None, 11, 3, -2, None, 1])
    first = path_sum_count(t, 8)
    second = path_sum_count(t, 8)
    other = path_sum_count(build([1, 2, 3]), 3)
    assert first == second == 3, (
        f"the same call twice gave {first} and {second}: keep the dictionary and the total INSIDE the function, "
        "so every call starts fresh.")
    assert other == 2, f"after the other calls, [1, 2, 3] with target 3 should give 2, got {other}."


def test_it_is_one_pass_not_a_new_walk_from_every_node():
    n = 4095                                          # a perfect tree with 12 levels, every value 1
    want = slow_count(build([1] * n), 3)
    t = build([1] * n, make=Counting)
    Counting.reads = 0
    got = path_sum_count(t, 3)
    reads = Counting.reads
    assert got == want, f"on a perfect tree of 4,095 ones the number of paths with sum 3 is {want}, got {got}."
    assert reads <= 8 * n, (
        f"your function read {reads:,} child pointers on a tree of {n:,} nodes; one pass needs only about {2 * n:,}. "
        "You probably start a new downward walk at every node (O(n * h)). Keep a dictionary of the running sums "
        "on the current root path instead.")
