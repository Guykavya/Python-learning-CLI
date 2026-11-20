import random
from collections import deque

import pytest

from solution import TreeNode, evaluate


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


def infix(node):
    """The test's own fully bracketed text of the expression, to be checked with Python's eval."""
    if node.left is None and node.right is None:
        return f"({node.val})"
    return f"({infix(node.left)} {node.val} {infix(node.right)})"


def random_expression(rng, depth):
    if depth == 0 or rng.random() < 0.25:
        return TreeNode(rng.randint(-9, 9))
    return TreeNode(rng.choice(["+", "-", "*", "/"]), random_expression(rng, depth - 1), random_expression(rng, depth - 1))


@pytest.mark.parametrize("values, expected", [
    ([7], 7),
    ([-5], -5),
    (["+", 3, 4], 7),
    (["-", 10, 4], 6),
    (["-", 2, 5], -3),
    (["*", 6, 7], 42),
    (["/", 7, 2], 3.5),
    (["/", 8, 4], 2),
    (["*", "+", 2, 3, 4], 14),
    (["+", "*", "-", 2, 3, 4, 5], 5),
    (["-", "*", "+", 6, 2, 1, 3], 8),
])
def test_examples(values, expected):
    t = build(values)
    got = evaluate(t)
    assert got == pytest.approx(expected), (
        f"the expression {infix(t)} is {expected}, got {got}. Evaluate both children first (postorder), "
        "then apply the operator with the LEFT value as the first operand.")


def test_negative_numbers_are_leaves():
    got = evaluate(build(["+", -3, 5]))
    assert got == 2, f"-3 + 5 is 2, got {got}. A leaf is a node with no children; a leaf can hold a negative number or 0."
    got = evaluate(build(["*", 0, 9]))
    assert got == 0, f"0 * 9 is 0, got {got}. A leaf with the value 0 is still a leaf."


def test_the_order_of_the_operands_matters():
    assert evaluate(build(["-", 1, 2])) == -1, "1 - 2 is -1: the left child is the first operand."
    assert evaluate(build(["/", 1, 4])) == pytest.approx(0.25), "1 / 4 is 0.25: the left child is the numerator, and the division is true division."


def test_random_expressions_against_eval():
    rng = random.Random(22)
    checked = 0
    while checked < 200:
        t = random_expression(rng, 4)
        try:
            want = eval(infix(t))
        except ZeroDivisionError:
            continue
        got = evaluate(t)
        assert got == pytest.approx(want), f"the expression {infix(t)} is {want}, got {got}."
        checked += 1
