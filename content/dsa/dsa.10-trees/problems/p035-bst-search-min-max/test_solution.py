import random
from collections import deque

import pytest

from solution import TreeNode, search, find_min, find_max


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


class Counting(TreeNode):
    """A TreeNode that counts how often its left and right pointers are READ (assigning is free)."""
    reads = 0

    def __init__(self, val=0, left=None, right=None):
        self._left = None
        self._right = None
        super().__init__(val, left, right)

    @property
    def left(self):
        Counting.reads += 1
        return self._left

    @left.setter
    def left(self, node):
        self._left = node

    @property
    def right(self):
        Counting.reads += 1
        return self._right

    @right.setter
    def right(self, node):
        self._right = node


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


def test_empty_tree():
    assert search(None, 5) is None, "An empty tree contains nothing: return None."
    assert find_min(None) is None, "An empty tree has no minimum: return None."
    assert find_max(None) is None, "An empty tree has no maximum: return None."


def test_example_tree():
    t = make_bst([4, 2, 6, 1, 3, 5, 7])
    by_val = {n.val: n for n in nodes(t)}
    for key in range(1, 8):
        got = search(t, key)
        assert got is by_val[key], (
            f"search(t, {key}) should return the node with value {key} (the node object itself), got {got!r}. "
            "Return the node, not cur.val.")
    for key in (0, 8, -3, 100):
        assert search(t, key) is None, f"{key} is not in the tree: search should return None."
    assert find_min(t) is by_val[1], "the minimum is the leftmost node (value 1)."
    assert find_max(t) is by_val[7], "the maximum is the rightmost node (value 7)."


def test_single_node_and_zero_and_negative_keys():
    t = build([0])
    assert search(t, 0) is t, "the key 0 is a real key: do not test the key with `if key:`."
    assert search(t, 1) is None, "the only key is 0, so 1 is not in the tree: None."
    assert find_min(t) is t and find_max(t) is t, "in a single node tree the node is both minimum and maximum."
    t = make_bst([-5, -10, 0, -7, 3])
    assert search(t, -7).val == -7 and search(t, -8) is None, "negative keys follow the same rule."
    assert find_min(t).val == -10 and find_max(t).val == 3, "the minimum is -10 and the maximum is 3."


def right_chain_bst(n):
    """1 -> 2 -> ... -> n: every node has only a right child."""
    root = None
    for v in range(n, 0, -1):
        root = TreeNode(v, None, root)
    return root


def left_chain_bst(n):
    """n at the root, n-1 as its left child, ... 1 at the bottom: every node has only a left child."""
    root = None
    for v in range(1, n + 1):
        root = TreeNode(v, root, None)
    return root


def test_chains():
    right, left = right_chain_bst(300), left_chain_bst(300)
    assert find_min(right).val == 1 and find_max(right).val == 300, "a chain that goes right: the minimum is the root."
    assert find_min(left).val == 1 and find_max(left).val == 300, "a chain that goes left: the maximum is the root."
    assert search(right, 300).val == 300 and search(left, 1).val == 1 and search(left, 301) is None, (
        "search must also work on a chain.")


def test_random_trees_against_a_sorted_list():
    rng = random.Random(35)
    for _ in range(200):
        keys = rng.sample(range(-30, 60), rng.randint(0, 25))
        t = make_bst(keys)
        by_val = {n.val: n for n in nodes(t)}
        for key in range(-32, 62, 3):
            want = by_val.get(key)
            got = search(t, key)
            assert got is want, f"keys inserted in this order: {keys}. search(t, {key}) should be the node {key!r} or None."
        if keys:
            assert find_min(t).val == min(keys), f"keys {keys}: the minimum is {min(keys)}."
            assert find_max(t).val == max(keys), f"keys {keys}: the maximum is {max(keys)}."


def test_the_tree_is_not_changed():
    t = make_bst([5, 3, 8, 1, 4, 7, 9])
    before = to_level(t)
    search(t, 4), search(t, 6), find_min(t), find_max(t)
    assert to_level(t) == before, "searching must not change the tree."


def test_it_walks_one_path_not_the_whole_tree():
    n = 4095                                          # a perfect BST: 12 levels
    level = to_level(balanced_bst(list(range(n))))
    t = build(level, make=Counting)
    Counting.reads = 0
    for key in (0, 1000, 2047, 4094, 4095, -1):
        search(t, key)
    reads = Counting.reads
    assert reads <= 6 * 4 * 13, (
        f"six searches read {reads:,} child pointers; each search needs at most about 13 (one per level). "
        "Do not walk the whole tree: compare the key and move to ONE child.")
    Counting.reads = 0
    find_min(t), find_max(t)
    reads = Counting.reads
    assert reads <= 2 * 4 * 13, (
        f"find_min and find_max read {reads:,} child pointers on a tree of 4,095 nodes. The minimum is the leftmost "
        "node and the maximum the rightmost: walk down one side only.")
