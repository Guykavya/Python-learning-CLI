import random
from collections import deque

import pytest

from solution import TreeNode, sorted_to_bst


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


def heights_balanced(root):
    """(balanced everywhere?, height in nodes) with the test's own recursion (depth about log n)."""
    if root is None:
        return True, 0
    ok_l, h_l = heights_balanced(root.left)
    ok_r, h_r = heights_balanced(root.right)
    return ok_l and ok_r and abs(h_l - h_r) <= 1, 1 + max(h_l, h_r)


def test_empty_and_single():
    assert sorted_to_bst([]) is None, "an empty list gives the empty tree: None."
    t = sorted_to_bst([5])
    assert t is not None and t.val == 5 and t.left is None and t.right is None, "one value: a single node."


def test_seven_values_give_the_perfect_tree():
    t = sorted_to_bst([1, 2, 3, 4, 5, 6, 7])
    assert to_level(t) == [4, 2, 6, 1, 3, 5, 7], (
        f"seven values: the middle (4) is the root, then the middle of each half: [4, 2, 6, 1, 3, 5, 7]; got {to_level(t)}.")


@pytest.mark.parametrize("n", [2, 3, 4, 5, 6, 8, 10, 15, 16, 31, 100, 1000, 5000])
def test_properties_for_many_sizes(n):
    values = list(range(10, 10 + 3 * n, 3))
    copy = list(values)
    t = sorted_to_bst(values)
    assert values == copy, "do not change the list you were given."
    assert inorder_vals(t) == values, (
        f"{n} values: the inorder traversal of your tree must be the list itself, in order and with no value lost or repeated.")
    assert is_bst_ref(t), "the tree is not a BST: smaller values must be on the left, larger on the right."
    balanced, height = heights_balanced(t)
    assert balanced, (
        f"{n} values: at some node the heights of the two subtrees differ by more than 1. "
        "Take the MIDDLE value as the root, not the first or the last.")
    assert height == n.bit_length(), (
        f"{n} values can be stored in a tree of height {n.bit_length()}, yours has height {height}.")


def test_negative_and_mixed_values():
    values = [-9, -4, 0, 3, 8, 21]
    t = sorted_to_bst(values)
    assert inorder_vals(t) == values and is_bst_ref(t), "negative values follow the same rule."
    assert heights_balanced(t) == (True, 3), "six values need a tree of height 3, balanced at every node."


def test_every_value_is_in_exactly_one_new_node():
    t = sorted_to_bst([1, 2, 3])
    assert isinstance(t, TreeNode), "build TreeNode objects (the class in your file)."
    assert {n.val for n in nodes(t)} == {1, 2, 3}, "each value must appear in exactly one node."
