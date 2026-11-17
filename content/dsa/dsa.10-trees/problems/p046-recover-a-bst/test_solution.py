import random
from collections import deque

import pytest

from solution import TreeNode, recover_tree


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


def inorder_nodes(root):
    out, stack, cur = [], [], root
    while cur is not None or stack:
        while cur is not None:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        out.append(cur)
        cur = cur.right
    return out


def test_the_two_examples():
    t = build([1, 3, None, None, 2])
    got = recover_tree(t)
    assert got is None, "recover_tree repairs the tree in place and returns nothing."
    assert to_level(t) == [3, 1, None, None, 2], (
        f"3 and 1 were swapped (far apart in the inorder list [3, 2, 1]); expected [3, 1, None, None, 2], got {to_level(t)}.")
    t = build([3, 1, 4, None, None, 2])
    recover_tree(t)
    assert to_level(t) == [2, 1, 4, None, None, 3], (
        f"3 and 2 were swapped (neighbours in the sorted order, one descent in [1, 3, 2, 4]); "
        f"expected [2, 1, 4, None, None, 3], got {to_level(t)}.")


def test_two_nodes_only():
    t = build([1, 2])                      # the BST [2, 1] with the two values swapped
    recover_tree(t)
    assert to_level(t) == [2, 1], f"expected [2, 1], got {to_level(t)}."


def test_the_root_and_a_leaf_swapped():
    t = make_bst([4, 2, 6, 1, 3, 5, 7])
    a, b = t, t.right.right                # the root 4 and the leaf 7
    a.val, b.val = b.val, a.val
    recover_tree(t)
    assert to_level(t) == [4, 2, 6, 1, 3, 5, 7], (
        f"the root and the largest leaf were swapped; the tree should be [4, 2, 6, 1, 3, 5, 7], got {to_level(t)}. "
        "Two descents: the second wrong node is the smaller side of the LAST descent.")


def test_random_swaps_neighbours_and_far_apart():
    rng = random.Random(47)
    for trial in range(400):
        keys = rng.sample(range(100), rng.randint(2, 25))
        t = make_bst(keys)
        original = to_level(t)
        ids = [id(n) for n in nodes(t)]
        in_order = inorder_nodes(t)
        i = rng.randrange(len(in_order) - 1)
        j = i + 1 if trial % 2 == 0 else rng.randrange(len(in_order))
        if i == j:
            j = (i + 1) % len(in_order)
        in_order[i].val, in_order[j].val = in_order[j].val, in_order[i].val
        broken = to_level(t)
        recover_tree(t)
        assert to_level(t) == original, (
            f"the BST {original} was damaged by swapping the values at inorder positions {min(i, j)} and "
            f"{max(i, j)}: {broken}. After recover_tree it is {to_level(t)}; it should be the original.")
        assert [id(n) for n in nodes(t)] == ids, "no node may move: change only the val fields."


def test_neighbours_in_the_sorted_order_have_one_descent_only():
    t = make_bst([5, 3, 8, 1, 4, 7, 9])
    in_order = inorder_nodes(t)             # values 1 3 4 5 7 8 9
    in_order[3].val, in_order[4].val = in_order[4].val, in_order[3].val    # 5 and 7
    recover_tree(t)
    assert to_level(t) == [5, 3, 8, 1, 4, 7, 9], (
        f"5 and 7 (neighbours in the sorted order) were swapped; expected [5, 3, 8, 1, 4, 7, 9], got {to_level(t)}. "
        "With one descent the two wrong nodes are the two sides of that descent.")
