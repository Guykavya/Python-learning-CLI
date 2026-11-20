import random
from collections import deque

import pytest

from solution import TreeNode, delete


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


def delete_ref(root, key):
    """The test's own delete (a loop, successor rule). It changes the tree it is given."""
    parent, cur = None, root
    while cur is not None and cur.val != key:
        parent, cur = cur, (cur.left if key < cur.val else cur.right)
    if cur is None:
        return root
    if cur.left is not None and cur.right is not None:
        succ_parent, succ = cur, cur.right
        while succ.left is not None:
            succ_parent, succ = succ, succ.left
        cur.val = succ.val
        parent, cur = succ_parent, succ              # the successor node has no left child
    child = cur.left if cur.left is not None else cur.right
    if parent is None:
        return child
    if parent.left is cur:
        parent.left = child
    else:
        parent.right = child
    return root


def test_empty_and_single_node():
    assert delete(None, 3) is None, "deleting from an empty tree leaves an empty tree."
    assert delete(build([5]), 5) is None, "deleting the only node leaves an empty tree: return None."
    t = build([5])
    assert delete(t, 9) is t and to_level(t) == [5], "a key that is not in the tree changes nothing."


def test_the_chapter_example_step_by_step():
    root = make_bst([5, 3, 8, 1, 4, 7, 9, 2])
    assert to_level(root) == [5, 3, 8, 1, 4, 7, 9, None, 2], "test data check."
    steps = [(4, [5, 3, 8, 1, None, 7, 9, None, 2], "a leaf: just remove it"),
             (1, [5, 3, 8, 2, None, 7, 9], "one child: the child 2 takes its place"),
             (5, [7, 3, 8, 2, None, None, 9], "two children: the successor 7 goes to the root and the old 7 is removed"),
             (42, [7, 3, 8, 2, None, None, 9], "not in the tree: nothing changes")]
    for key, want, why in steps:
        root = delete(root, key)
        assert to_level(root) == want, f"after delete {key} ({why}) the tree should be {want}, got {to_level(root)}."


def test_two_children_with_a_deep_successor():
    root = make_bst([50, 30, 70, 20, 40, 60, 80, 65])
    root = delete(root, 50)
    assert to_level(root) == [60, 30, 70, 20, 40, 65, 80], (
        f"deleting 50: the successor is 60 (the leftmost node of the right subtree). The value 60 goes to the root and "
        f"the old node 60 (the left child of 70) is replaced by its only child 65. Got {to_level(root)}. "
        "Remember to delete the successor node, and to keep ITS right subtree.")


def test_one_child_keeps_the_whole_subtree():
    root = make_bst([10, 5, 20, 7, 6, 8])             # 5 has only a right child: 7, which has the children 6 and 8
    root = delete(root, 5)
    assert to_level(root) == [10, 7, 20, 6, 8], (
        f"5 has one child (7, with its children 6 and 8): that whole subtree moves up under 10. "
        f"Expected [10, 7, 20, 6, 8], got {to_level(root)}.")


def test_deleting_the_root_with_one_child():
    root = make_bst([2, 1])
    root = delete(root, 2)
    assert to_level(root) == [1], f"the root has only a left child: that child becomes the root, got {to_level(root)}."
    root = make_bst([2, 3, 4])
    root = delete(root, 2)
    assert to_level(root) == [3, None, 4], f"the root has only a right child: that child becomes the root, got {to_level(root)}."


def test_random_operations_against_a_set():
    rng = random.Random(37)
    mine, ref, model = None, None, set()
    for step in range(3000):
        key = rng.randint(0, 40)
        if rng.random() < 0.55:
            mine, ref = insert_ref(mine, key), insert_ref(ref, key)
            model.add(key)
            continue
        mine = delete(mine, key)
        ref = delete_ref(ref, key)
        model.discard(key)
        got = inorder_vals(mine)
        assert got == sorted(model), (
            f"step {step}: after delete({key}) the keys in the tree should be {sorted(model)}, got {got}. "
            "A subtree was lost, or a key was left in the tree twice.")
        assert to_level(mine) == to_level(ref), (
            f"step {step}: after delete({key}) the tree should be {to_level(ref)}, got {to_level(mine)}. "
            "For two children use the SUCCESSOR (the smallest key of the right subtree).")


def test_a_chain_of_300_nodes():
    root = None
    for k in range(1, 301):
        root = insert_ref(root, k)
    for key in (1, 300, 150):
        root = delete(root, key)
    assert inorder_vals(root) == [k for k in range(1, 301) if k not in (1, 300, 150)], (
        "after deleting 1, 300 and 150 from a chain 1..300 the other 297 keys must remain, in order.")
