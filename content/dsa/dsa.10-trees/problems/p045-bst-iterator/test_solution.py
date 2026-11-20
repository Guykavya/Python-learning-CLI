import random
from collections import deque

import pytest

from solution import TreeNode, BSTIterator


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


def drain(it):
    out = []
    while it.has_next():
        out.append(it.next())
    return out


def test_empty_tree():
    it = BSTIterator(None)
    assert it.has_next() is False, "An empty tree has no next value: has_next() must return False."
    with pytest.raises(StopIteration):
        it.next()


def test_the_example_step_by_step():
    it = BSTIterator(build([7, 3, 15, None, None, 9, 20]))
    assert it.next() == 3, "the smallest value comes first: 3."
    assert it.next() == 7, "the next one is 7."
    assert it.has_next() is True, "9, 15 and 20 are still waiting."
    assert (it.next(), it.next(), it.next()) == (9, 15, 20), "then 9, 15, 20 in increasing order."
    assert it.has_next() is False, "all values were returned: has_next() must be False."
    with pytest.raises(StopIteration):
        it.next()


def test_has_next_does_not_move_the_iterator():
    it = BSTIterator(make_bst([2, 1, 3]))
    assert it.has_next() is True and it.has_next() is True, "calling has_next() twice must not skip a value."
    assert drain(it) == [1, 2, 3], "after two has_next() calls the walk must still give 1, 2, 3."


def test_random_trees_in_order_and_unchanged():
    rng = random.Random(45)
    for _ in range(200):
        keys = rng.sample(range(-30, 70), rng.randint(0, 30))
        t = make_bst(keys)
        before = to_level(t)
        got = drain(BSTIterator(t))
        assert got == sorted(keys), f"keys {keys}: the walk should give {sorted(keys)}, got {got}."
        assert to_level(t) == before, "the iterator must not change the tree."


def test_two_iterators_on_the_same_tree_are_independent():
    t = make_bst([4, 2, 6, 1, 3, 5, 7])
    a, b = BSTIterator(t), BSTIterator(t)
    first = [a.next(), a.next(), a.next()]
    second = drain(b)
    rest = drain(a)
    assert first == [1, 2, 3] and second == [1, 2, 3, 4, 5, 6, 7] and rest == [4, 5, 6, 7], (
        f"two iterators must not share their state (keep the stack in self, not in the class): "
        f"got {first}, {second}, {rest}.")


def test_random_mixes_of_next_and_has_next():
    rng = random.Random(46)
    keys = rng.sample(range(200), 60)
    t = make_bst(keys)
    it, want, pos = BSTIterator(t), sorted(keys), 0
    for _ in range(300):
        if rng.random() < 0.5:
            assert it.has_next() is (pos < len(want)), f"has_next() after {pos} values should be {pos < len(want)}."
        elif pos < len(want):
            assert it.next() == want[pos], f"the value number {pos + 1} should be {want[pos]}."
            pos += 1
        else:
            with pytest.raises(StopIteration):
                it.next()


def test_it_is_lazy_and_cheap():
    n = 4095
    t = build(to_level(balanced_bst(list(range(n)))), make=Counting)
    Counting.reads = 0
    it = BSTIterator(t)
    first = [it.next(), it.next(), it.next()]
    reads = Counting.reads
    assert first == [0, 1, 2], f"the first three values of 0..4094 are 0, 1, 2, got {first}."
    assert reads <= 120, (
        f"creating the iterator and taking three values read {reads:,} child pointers on a tree of {n:,} nodes; "
        "about 30 are enough. Do not walk the whole tree in the constructor and keep a list of all values: "
        "keep only the stack of waiting nodes (O(h) memory).")
    Counting.reads = 0
    rest = drain(it)
    reads = Counting.reads
    assert rest == list(range(3, n)), "the rest of the walk must give 3..4094."
    assert reads <= 6 * n, f"the whole walk read {reads:,} pointers; every node should be pushed and popped once (about {2 * n:,})."
