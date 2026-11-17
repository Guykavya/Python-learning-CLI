import random
from collections import deque

import pytest

from solution import TreeNode, is_valid_bst


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


def insert_ref(root, key):
    """The test's own BST insert (a loop, duplicates ignored). Returns the root."""
    node = TreeNode(key)
    if root is None:
        return node
    cur = root
    while True:
        if key == cur.val:
            return root
        side = "left" if key < cur.val else "right"
        nxt = getattr(cur, side)
        if nxt is None:
            setattr(cur, side, node)
            return root
        cur = nxt


def make_bst(keys):
    """A BST made by inserting the keys one after the other (the shape depends on the order)."""
    root = None
    for k in keys:
        root = insert_ref(root, k)
    return root


def balanced_bst(keys, make=TreeNode):
    """A BST of minimal height for the SORTED list `keys` (the middle key is the root)."""
    def go(lo, hi):
        if lo >= hi:
            return None
        mid = (lo + hi) // 2
        return make(keys[mid], go(lo, mid), go(mid + 1, hi))
    return go(0, len(keys))


def inorder_vals(root):
    """The test's own inorder walk (a loop with a stack)."""
    out, stack, cur = [], [], root
    while cur is not None or stack:
        while cur is not None:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        out.append(cur.val)
        cur = cur.right
    return out


def is_bst_ref(root):
    """True if the inorder values are strictly increasing."""
    vals = inorder_vals(root)
    return all(a < b for a, b in zip(vals, vals[1:]))


def valid_brute(node):
    """The definition: everything in the left subtree < node < everything in the right subtree."""
    if node is None:
        return True
    left, right = nodes(node.left), nodes(node.right)
    return (all(n.val < node.val for n in left) and all(n.val > node.val for n in right)
            and valid_brute(node.left) and valid_brute(node.right))


@pytest.mark.parametrize("values, expected", [
    ([], True),
    ([7], True),
    ([2, 1, 3], True),
    ([4, 2, 6, 1, 3, 5, 7], True),
    ([5, 1, 4], False),
    ([2, 3, 1], False),
    ([2, 2, 2], False),
    ([2, 1, 2], False),
    ([2, 2], False),
    ([2, None, 2], False),
])
def test_small_trees(values, expected):
    got = is_valid_bst(build(values))
    assert got is expected, (
        f"is_valid_bst({values}) should be {expected}, got {got}. Smaller values on the left, larger on the right, "
        "and equal values are not allowed.")


@pytest.mark.parametrize("values", [
    [5, 1, 6, None, None, 3, 7],
    [10, 5, 15, None, None, 6, 20],
    [10, 5, 15, None, 12],
    [20, 10, 30, 5, 25],
    [8, 4, 12, 2, 6, 10, 14, 1, 3, 5, 9],
])
def test_a_node_that_is_fine_against_its_parent_but_not_against_an_ancestor(values):
    got = is_valid_bst(build(values))
    assert got is False, (
        f"{values} is NOT a BST, but your function said {got}. Some node is correct next to its parent and wrong "
        "against an ancestor. Pass a lower and an upper bound down (going left sets the upper bound, going right the lower bound).")


def test_values_at_and_beyond_the_int_limits():
    lo, hi = -2147483648, 2147483647
    cases = [([hi], True), ([lo], True), ([lo, None, hi], True), ([0, lo, hi], True),
             ([hi, hi], False), ([hi, None, hi], False), ([lo, lo], False),
             ([2 ** 70], True), ([-(2 ** 70), None, 2 ** 70], True), ([0, 2 ** 70, -(2 ** 70)], False)]
    for values, expected in cases:
        got = is_valid_bst(build(values))
        assert got is expected, (
            f"is_valid_bst({values}) should be {expected}, got {got}. Do not use 2**31 - 1 or -2**31 as 'infinity': "
            "a tree can hold exactly that number. Use None for 'no bound'.")


def test_random_trees_against_the_definition():
    rng = random.Random(38)
    valid_seen = 0
    for i in range(600):
        if i % 3 == 0:
            t = random_tree(rng, rng.randint(0, 9), 0, 6)
        else:
            t = make_bst(rng.sample(range(30), rng.randint(0, 9)))
            all_nodes = nodes(t)
            if i % 3 == 2 and len(all_nodes) > 1:                # break a real BST: swap two values
                a, b = rng.sample(all_nodes, 2)
                a.val, b.val = b.val, a.val
        want = valid_brute(t)
        valid_seen += want
        got = is_valid_bst(t)
        assert got is want, f"the tree {to_level(t)}: is_valid_bst should be {want}, got {got}."
    assert valid_seen > 100, "test data check: the random trees must contain many valid BSTs."


def test_a_long_chain():
    n = 400
    good = right_chain(n)                              # 1 -> 2 -> ... -> 400: a valid BST
    assert is_valid_bst(good) is True, "a sorted chain 1, 2, ..., 400 is a valid BST."
    bad = right_chain(n)
    last = bad
    while last.right is not None:
        last = last.right
    last.val = 0                                       # the last node is smaller than all its ancestors
    assert is_valid_bst(bad) is False, "the last node (0) is smaller than every ancestor: the tree is not a BST."
    zig = zigzag_chain(n)
    assert is_valid_bst(zig) is False, "1, then 2 on its LEFT: a left child larger than its parent is invalid."
