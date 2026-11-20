import random
from collections import deque

import pytest

from solution import TreeNode, flatten


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


def chain_values(root):
    out = []
    while root is not None:
        out.append(root.val)
        root = root.right
        if len(out) > 100000:
            raise AssertionError("the right pointers do not end: the 'list' has a cycle.")
    return out


def preorder_nodes(root):
    """The node objects in preorder (a loop with a stack)."""
    out, stack = [], [root] if root is not None else []
    while stack:
        node = stack.pop()
        out.append(node)
        for child in (node.right, node.left):
            if child is not None:
                stack.append(child)
    return out


def check_flat(root, expected_nodes, what):
    chain, node = [], root
    while node is not None and len(chain) <= len(expected_nodes):
        chain.append(node)
        node = node.right
    assert node is None and len(chain) == len(expected_nodes), (
        f"{what}: following the right pointers should visit {len(expected_nodes)} nodes, but it visited "
        f"{len(chain)}{' and did not end' if node is not None else ''}. A subtree was lost or linked twice.")
    assert [id(n) for n in chain] == [id(n) for n in expected_nodes], (
        f"{what}: the nodes are not in the preorder of the original tree. "
        f"Expected the values {[n.val for n in expected_nodes]}, got {[n.val for n in chain]}.")
    assert all(n.left is None for n in chain), f"{what}: every node must have left = None."


def test_empty_and_single():
    assert flatten(None) is None, "flatten(None) does nothing."
    t = build([7])
    flatten(t)
    assert t.val == 7 and t.left is None and t.right is None, "a single node stays as it is."


def test_the_chapter_example():
    t = build([1, 2, 5, 3, 4, None, 6])
    expected = preorder_nodes(t)
    flatten(t)
    assert chain_values(t) == [1, 2, 3, 4, 5, 6], (
        f"[1, 2, 5, 3, 4, None, 6] should become the right chain 1, 2, 3, 4, 5, 6, got {chain_values(t)}.")
    check_flat(t, expected, "the chapter example")


def test_only_a_left_child_and_only_right_children():
    t = build([1, 2])
    exp = preorder_nodes(t)
    flatten(t)
    check_flat(t, exp, "[1, 2]: a node with only a left child")
    t = build([1, None, 2, None, 3])
    exp = preorder_nodes(t)
    flatten(t)
    check_flat(t, exp, "a tree that is already a right chain")


def test_the_old_right_subtree_goes_after_the_whole_left_subtree():
    t = build([1, 2, 3, 4, 5, 6, 7])
    flatten(t)
    assert chain_values(t) == [1, 2, 4, 5, 3, 6, 7], (
        f"preorder of a perfect tree of 7 nodes is 1, 2, 4, 5, 3, 6, 7; got {chain_values(t)}. "
        "The right subtree 3, 6, 7 must come after the LAST node (5) of the left subtree.")


def test_random_trees_keep_the_same_node_objects_in_preorder():
    rng = random.Random(58)
    for _ in range(300):
        t = random_tree(rng, rng.randint(1, 30))
        expected = preorder_nodes(t)
        before = to_level(t)
        flatten(t)
        check_flat(t, expected, f"the tree {before}")


def test_long_chains():
    for make in (left_chain, right_chain, zigzag_chain):
        t = make(300)
        expected = preorder_nodes(t)
        flatten(t)
        check_flat(t, expected, f"a chain of 300 nodes ({make.__name__})")
