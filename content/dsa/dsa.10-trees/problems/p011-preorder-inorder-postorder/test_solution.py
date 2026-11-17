import random
from collections import deque

import pytest

from solution import TreeNode, preorder, inorder, postorder


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


def reference_order(root, order):
    """The test's own traversal (an explicit stack of (node, done) pairs, the chapter's one template)."""
    out, stack = [], [(root, False)]
    while stack:
        node, done = stack.pop()
        if node is None:
            continue
        if done:
            out.append(node.val)
        elif order == "pre":
            stack += [(node.right, False), (node.left, False), (node, True)]
        elif order == "in":
            stack += [(node.right, False), (node, True), (node.left, False)]
        else:
            stack += [(node, True), (node.right, False), (node.left, False)]
    return out


BST = [4, 2, 6, 1, 3, 5, 7]


def test_empty_tree():
    assert preorder(None) == [], "preorder of an empty tree is []."
    assert inorder(None) == [], "inorder of an empty tree is []."
    assert postorder(None) == [], "postorder of an empty tree is []."


def test_preorder_example():
    got = preorder(build(BST))
    assert got == [4, 2, 1, 3, 6, 5, 7], f"preorder is node, left, right: [4, 2, 1, 3, 6, 5, 7], got {got}."


def test_inorder_example():
    got = inorder(build(BST))
    assert got == [1, 2, 3, 4, 5, 6, 7], f"inorder is left, node, right: [1, 2, 3, 4, 5, 6, 7], got {got}."


def test_postorder_example():
    got = postorder(build(BST))
    assert got == [1, 3, 2, 5, 7, 6, 4], f"postorder is left, right, node: [1, 3, 2, 5, 7, 6, 4], got {got}."


@pytest.mark.parametrize("values, pre, ino, post", [
    ([1, None, 2, 3], [1, 2, 3], [1, 3, 2], [3, 2, 1]),
    ([1, 2, 3, 4, 5], [1, 2, 4, 5, 3], [4, 2, 5, 1, 3], [4, 5, 2, 3, 1]),
    ([7], [7], [7], [7]),
    ([1, 2, None, 3], [1, 2, 3], [3, 2, 1], [3, 2, 1]),
])
def test_small_trees(values, pre, ino, post):
    t = build(values)
    assert preorder(t) == pre, f"preorder of {values} should be {pre}, got {preorder(t)}."
    assert inorder(t) == ino, f"inorder of {values} should be {ino}, got {inorder(t)}."
    assert postorder(t) == post, f"postorder of {values} should be {post}, got {postorder(t)}."


def test_two_calls_give_the_same_answer():
    t = build(BST)
    for f in (preorder, inorder, postorder):
        first = f(t)
        second = f(t)
        assert first == second, (
            f"{f.__name__} gave {first} and then {second} for the same tree: a list kept outside the function "
            "remembers the old values. Create the list inside the function.")
        assert len(second) == 7, f"{f.__name__} must return exactly the 7 values of the tree, got {len(second)}."


def test_random_trees_against_the_reference_orders():
    rng = random.Random(11)
    for _ in range(200):
        t = random_tree(rng, rng.randint(0, 30))
        for name, f in (("pre", preorder), ("in", inorder), ("post", postorder)):
            want = reference_order(t, name)
            got = f(t)
            assert got == want, f"{f.__name__} of the tree {to_level(t)} should be {want}, got {got}."
