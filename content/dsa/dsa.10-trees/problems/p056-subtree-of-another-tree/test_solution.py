import random
from collections import deque

import pytest

from solution import TreeNode, is_subtree


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


def is_subtree_brute(root, sub):
    """Every node of root, compared with sub through the level-order lists."""
    if sub is None:
        return True
    return any(to_level(n) == to_level(sub) for n in nodes(root))


def test_empty_cases():
    assert is_subtree(None, None) is True, "the empty tree is a subtree of the empty tree."
    assert is_subtree(build([1, 2]), None) is True, "the empty tree is a subtree of every tree."
    assert is_subtree(None, build([1])) is False, "an empty tree contains no non-empty subtree."


@pytest.mark.parametrize("root, sub, expected", [
    ([3, 4, 5, 1, 2], [4, 1, 2], True),
    ([3, 4, 5, 1, 2, None, None, None, None, 0], [4, 1, 2], False),
    ([3, 4, 5, 1, 2], [3, 4, 5, 1, 2], True),
    ([3, 4, 5, 1, 2], [3, 4, 5], False),
    ([3, 4, 5, 1, 2], [5], True),
    ([3, 4, 5, 1, 2], [6], False),
    ([1, 1], [1], True),
    ([1, 1], [1, None, 1], False),
    ([1, None, 1], [1, 1], False),
    ([1], [1, 1], False),
    ([12], [2], False),
    ([3, 12, 1], [2], False),
    ([3, 12, 1], [12], True),
    ([1, 2, 3, 4], [2, 4], True),
])
def test_examples(root, sub, expected):
    got = is_subtree(build(root), build(sub))
    assert got is expected, (
        f"is_subtree({root}, {sub}) should be {expected}, got {got}. A subtree contains ALL the descendants of its top "
        "node, so compare the whole shape down to the leaves, at every node of the big tree.")


def test_random_trees_against_the_level_order_lists():
    rng = random.Random(57)
    true_seen = 0
    for i in range(600):
        big = random_tree(rng, rng.randint(1, 9), 0, 2)
        if i % 3 == 0:
            sub = build(to_level(rng.choice(nodes(big))))               # a real subtree (a copy)
        elif i % 3 == 1:
            sub = random_tree(rng, rng.randint(0, 3), 0, 2)
        else:
            sub = build(to_level(rng.choice(nodes(big))))
            if sub is not None and (sub.left is not None or sub.right is not None):
                sub.val += 1                                            # nearly a subtree
        want = is_subtree_brute(big, sub)
        true_seen += want
        got = is_subtree(big, sub)
        assert got is want, f"is_subtree({to_level(big)}, {to_level(sub)}) should be {want}, got {got}."
    assert true_seen > 100, "test data check: many cases must be real subtrees."


def test_a_long_chain():
    big = left_chain(300)
    sub = None                                       # the end of the chain: 151, 152, ..., 300, built with a loop
    for v in range(300, 150, -1):
        sub = TreeNode(v, sub, None)
    sub_wrong = None
    for v in range(301, 151, -1):
        sub_wrong = TreeNode(v, sub_wrong, None)
    assert is_subtree(big, sub) is True, "the end of the chain 1..300 (151..300) is a subtree of it."
    assert is_subtree(big, sub_wrong) is False, "the chain 152..301 is not a subtree: the values are different."
