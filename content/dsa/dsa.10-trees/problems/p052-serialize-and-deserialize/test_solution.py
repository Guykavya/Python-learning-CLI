import random
from collections import deque

import pytest

from solution import TreeNode, serialize, deserialize


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


def test_none_and_single_nodes():
    s = serialize(None)
    assert isinstance(s, str), f"serialize must return a string (str), got {type(s).__name__}: it has to be saved or sent."
    assert deserialize(s) is None, "the empty tree must round-trip to None."
    for value in (0, 7, -3, 1000000):
        t = deserialize(serialize(build([value])))
        assert t is not None and t.val == value and t.left is None and t.right is None, (
            f"a single node with the value {value} must round-trip; got {None if t is None else to_level(t)}.")


@pytest.mark.parametrize("values", [
    [1, 2, 3],
    [1, 2, 3, None, None, 4, 5],
    [1, None, 2],
    [1, 2],
    [1, None, 2, None, 3],
    [5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1],
    [-12, None, 0],
    [0, 0, 0, None, 0],
    [10, 1, 100, None, 2, 3],
    [-1, -2, -3, -4, None, None, -5],
])
def test_round_trip_examples(values):
    s = serialize(build(values))
    assert isinstance(s, str), "serialize must return a string."
    got = to_level(deserialize(s))
    assert got == values, (
        f"deserialize(serialize(tree)) should give back {values}, got {got}. "
        "Write a marker for every missing child and separate the tokens (so 1 and 2 do not run together as 12).")


def test_different_trees_give_different_strings():
    a, b = serialize(build([1, 2])), serialize(build([1, None, 2]))
    assert a != b, "the trees [1, 2] (2 on the left) and [1, None, 2] (2 on the right) must give different strings."


def test_random_trees_with_gaps_negative_and_large_values():
    rng = random.Random(52)
    for _ in range(400):
        t = random_tree(rng, rng.randint(0, 40), -2000, 2000)
        want = to_level(t)
        got = to_level(deserialize(serialize(t)))
        assert got == want, f"the tree {want} came back as {got} after serialize and deserialize."
    big = random_tree(rng, 30, -10 ** 12, 10 ** 12)
    assert to_level(deserialize(serialize(big))) == to_level(big), "large values (up to 10**12) must round-trip."


def test_the_string_carries_all_the_information():
    t = build([1, 2, 3])
    s = serialize(t)
    t.val = 99                                   # change the original after serialising
    t.left = None
    got = deserialize(s)
    assert to_level(got) == [1, 2, 3], (
        f"the string was made when the tree was [1, 2, 3], but deserialize returned {to_level(got)}. "
        "Do not keep the original tree in a variable: everything must be in the string.")


def test_every_call_builds_new_nodes():
    s = serialize(build([1, 2, 3]))
    a, b = deserialize(s), deserialize(s)
    ids_a = {id(n) for n in nodes(a)}
    ids_b = {id(n) for n in nodes(b)}
    assert to_level(a) == to_level(b) == [1, 2, 3], "the same string must give the same tree every time."
    assert not (ids_a & ids_b), "two calls of deserialize must build separate nodes (do not cache the tree)."


def test_long_chains():
    for make in (left_chain, right_chain, zigzag_chain):
        t = make(400)
        want = to_level(t)
        got = to_level(deserialize(serialize(t)))
        assert got == want, f"a chain of 400 nodes ({make.__name__}) did not round-trip."
