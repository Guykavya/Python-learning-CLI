import random
from collections import deque

import pytest

from solution import TreeNode, insert


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


def test_into_an_empty_tree():
    got = insert(None, 7)
    assert got is not None and got.val == 7, "inserting into an empty tree returns a new node holding the key."
    assert got.left is None and got.right is None, "the new node is a leaf."


def test_the_chapter_example_gives_the_exact_shape():
    root = None
    for key in (5, 3, 8, 1, 4, 7, 9, 2):
        root = insert(root, key)
    assert to_level(root) == [5, 3, 8, 1, 4, 7, 9, None, 2], (
        f"inserting 5, 3, 8, 1, 4, 7, 9, 2 in this order should give [5, 3, 8, 1, 4, 7, 9, None, 2], "
        f"got {to_level(root)}. Smaller keys go left, larger keys go right, the new node is a new leaf.")


def test_the_root_does_not_change_and_old_nodes_stay():
    root = make_bst([5, 3, 8])
    before = {id(n) for n in nodes(root)}
    got = insert(root, 4)
    assert got is root, "insert must return the same root when the tree was not empty (reattach the subtrees)."
    after = {id(n) for n in nodes(got)}
    assert before <= after and len(after) == len(before) + 1, (
        "the old nodes must stay the same objects and exactly one new node must appear.")


def test_a_duplicate_is_ignored():
    root = make_bst([5, 3, 8, 1])
    before = to_level(root)
    for key in (5, 3, 8, 1):
        got = insert(root, key)
        assert got is root and to_level(root) == before, (
            f"the key {key} is already in the tree {before}: the tree must stay the same, "
            f"but it is now {to_level(root)}. Do not add a duplicate on either side.")


def test_the_result_is_reattached_not_lost():
    root = make_bst([10])
    root = insert(root, 5)
    root = insert(root, 15)
    root = insert(root, 3)
    assert to_level(root) == [10, 5, 15, 3], (
        f"expected [10, 5, 15, 3], got {to_level(root)}. If a key is missing, you called insert(root.left, key) "
        "without assigning the result to root.left.")


def test_random_keys_give_the_same_tree_as_the_reference_insert():
    rng = random.Random(36)
    for _ in range(200):
        keys = [rng.randint(0, 40) for _ in range(rng.randint(0, 30))]
        root = None
        for k in keys:
            root = insert(root, k)
        want = make_bst(keys)
        assert to_level(root) == to_level(want), (
            f"keys inserted in this order: {keys}. The tree should be {to_level(want)}, got {to_level(root)}. "
            "Each new key is a new leaf; duplicates change nothing.")
        assert inorder_vals(root) == sorted(set(keys)), "the inorder traversal must be the sorted distinct keys."


def test_sorted_keys_make_a_chain():
    root = None
    for k in range(1, 301):
        root = insert(root, k)
    assert inorder_vals(root) == list(range(1, 301)), "300 sorted keys: the inorder must be 1..300."
    height, node = 0, root
    while node is not None:
        height, node = height + 1, node.right
    assert height == 300, "sorted insertion makes a chain to the right: every key is larger than the one before."
