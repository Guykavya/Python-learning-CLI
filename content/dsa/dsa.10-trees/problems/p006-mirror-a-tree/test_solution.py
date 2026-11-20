import random
from collections import deque

import pytest

from solution import TreeNode, invert


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


def mirror_copy(node):
    """The expected answer: a mirrored COPY made of new nodes (the test's own code)."""
    if node is None:
        return None
    return TreeNode(node.val, mirror_copy(node.right), mirror_copy(node.left))


def test_empty_tree():
    assert invert(None) is None, "invert(None) must return None."


def test_single_node():
    t = build([7])
    assert invert(t) is t, "A single node is its own mirror: return the same node."


def test_small_tree_values():
    got = invert(build([4, 2, 6, 1, 3, 5, 7]))
    assert to_level(got) == [4, 6, 2, 7, 5, 3, 1], (
        f"the mirror of [4, 2, 6, 1, 3, 5, 7] is [4, 6, 2, 7, 5, 3, 1], got {to_level(got)}. "
        "The swap must happen at EVERY node, not only at the root.")


def test_left_chain_becomes_right_chain():
    got = invert(build([1, 2, None, 3]))
    assert to_level(got) == [1, None, 2, None, 3], f"a left chain becomes a right chain, got {to_level(got)}."


def test_swap_does_not_lose_a_subtree():
    got = invert(build([1, 2, 3]))
    assert got.left is not got.right, (
        "both children are the same node: you overwrote root.left before saving it. "
        "Use root.left, root.right = invert(root.right), invert(root.left).")
    assert (got.left.val, got.right.val) == (3, 2), f"after the swap the children should be 3 and 2, got {got.left.val} and {got.right.val}."


def test_same_node_objects_in_place():
    t = build([4, 2, 6, 1, 3, 5, 7])
    before = {id(n) for n in nodes(t)}
    got = invert(t)
    assert got is t, "Return the same root node you were given: the tree is changed in place."
    after = {id(n) for n in nodes(got)}
    assert after == before, "The result must be made of the SAME node objects: do not create new nodes, rewire the old ones."


def test_random_trees_against_a_mirrored_copy():
    rng = random.Random(6)
    for _ in range(200):
        t = random_tree(rng, rng.randint(0, 30))
        want = to_level(mirror_copy(t))
        original = to_level(t)
        got = to_level(invert(t))
        assert got == want, f"the mirror of {original} should be {want}, got {got}."


def test_inverting_twice_gives_the_original():
    rng = random.Random(7)
    for _ in range(50):
        t = random_tree(rng, rng.randint(0, 30))
        original = to_level(t)
        again = to_level(invert(invert(t)))
        assert again == original, f"inverting twice must give the original {original}, got {again}."
