import random
from collections import deque

import pytest

from solution import TreeNode, iter_inorder


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


def perfect_search_tree(height):
    """Level-order list of a perfect search tree with the keys 1 .. 2**height - 1."""
    out, queue = [], deque([(1, 2 ** height - 1)])
    while queue:
        lo, hi = queue.popleft()
        mid = (lo + hi) // 2
        out.append(mid)
        if lo < hi:
            queue.append((lo, mid - 1))
            queue.append((mid + 1, hi))
    return out


def test_it_is_a_generator_not_a_list():
    g = iter_inorder(build([2, 1, 3]))
    assert not isinstance(g, list), "Return a generator (use yield), not a list: a list is built before the first value is known."
    assert hasattr(g, "__next__"), "iter_inorder(root) must return an iterator: a generator function with yield."
    assert next(g) == 1, "The first value of [2, 1, 3] in inorder is 1."


def test_empty_tree_yields_nothing():
    assert list(iter_inorder(None)) == [], "An empty tree yields no values."


@pytest.mark.parametrize("values, expected", [
    ([7], [7]),
    ([4, 2, 6, 1, 3, 5, 7], [1, 2, 3, 4, 5, 6, 7]),
    ([1, None, 2, 3], [1, 3, 2]),
    ([1, 2, 3, 4, 5], [4, 2, 5, 1, 3]),
])
def test_examples(values, expected):
    got = list(iter_inorder(build(values)))
    assert got == expected, f"the inorder values of {values} should be {expected}, got {got}."


def test_one_value_at_a_time():
    g = iter_inorder(build([4, 2, 6, 1, 3, 5, 7]))
    assert [next(g) for _ in range(3)] == [1, 2, 3], "The first three values must be 1, 2, 3."
    assert [next(g) for _ in range(4)] == [4, 5, 6, 7], "The generator must continue where it paused: 4, 5, 6, 7."
    with pytest.raises(StopIteration):
        next(g)


def test_random_trees():
    rng = random.Random(16)
    for _ in range(200):
        t = random_tree(rng, rng.randint(0, 30))
        want = reference_order(t, "in")
        got = list(iter_inorder(t))
        assert got == want, f"the inorder values of {to_level(t)} should be {want}, got {got}."


def test_taking_three_values_does_not_visit_the_whole_tree():
    n_levels = 15                                          # 32,767 nodes
    values = perfect_search_tree(n_levels)
    t = build(values, make=Counting)
    Counting.reads = 0
    g = iter_inorder(t)
    first = [next(g) for _ in range(3)]
    reads = Counting.reads
    assert first == [1, 2, 3], f"the first three inorder values are 1, 2, 3, got {first}."
    assert reads < 300, (
        f"to produce 3 values your generator read {reads} child pointers; the tree has 32,767 nodes (about 65,000 pointers). "
        "It does the whole walk before the first value. Use yield inside the walk, so the work stops when next() is not called.")
    assert sum(1 for _ in g) == 2 ** n_levels - 1 - 3, "after 3 values, the generator must still deliver all the remaining values."
