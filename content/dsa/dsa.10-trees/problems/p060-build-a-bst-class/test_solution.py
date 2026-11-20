import ast
import pathlib
import random
import sys
from collections import deque

import pytest

from solution import TreeNode, BST


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


def with_low_recursion_limit(f, *args, spare=80):
    """Call f with the recursion limit lowered to `spare` frames above the current depth.
    An iterative function needs a handful of frames; a recursive one on a long chain runs out."""
    depth, frame = 0, sys._getframe()
    while frame is not None:
        depth += 1
        frame = frame.f_back
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(depth + spare)
    try:
        return f(*args)
    except RecursionError:
        raise AssertionError(
            "RecursionError: a recursive method ran out of stack on a tree that is a chain of thousands of nodes. "
            "Sorted insertions make a chain, so write insert, delete, contains, height and inorder as loops.") from None
    finally:
        sys.setrecursionlimit(old)


SOLUTION = pathlib.Path(__file__).with_name("solution.py")


def test_no_shortcuts_in_the_code():
    tree = ast.parse(SOLUTION.read_text(encoding="utf-8"))
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    imports = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    imports |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    banned = (names | attrs | imports) & {"set", "frozenset", "sorted", "bisect", "insort", "setrecursionlimit", "sortedcontainers"}
    assert not banned, (
        f"your file uses {sorted(banned)}. Keep the keys in the tree (TreeNode objects) and do not hide a set or a "
        "sorted list behind the class; and do not raise the recursion limit: write loops.")


def test_an_empty_tree():
    t = BST()
    assert len(t) == 0, "a new tree has 0 keys."
    assert t.height() == 0, "an empty tree has height 0 (counted in nodes)."
    assert t.inorder() == [], "an empty tree has no keys."
    assert t.contains(1) is False, "an empty tree contains nothing."
    assert t.delete(1) is False, "deleting from an empty tree returns False."


def test_the_example_of_the_statement():
    t = BST()
    assert [t.insert(k) for k in (5, 3, 8, 1, 4, 7, 9, 2)] == [True] * 8, "new keys: insert returns True."
    assert (t.insert(4), len(t), t.height()) == (False, 8, 4), (
        "inserting 4 again returns False and changes nothing; the tree has 8 keys and height 4 (5 - 3 - 1 - 2).")
    assert t.inorder() == [1, 2, 3, 4, 5, 7, 8, 9], "inorder must be sorted."
    assert (t.delete(5), t.delete(42), t.contains(5), t.contains(7)) == (True, False, False, True), (
        "delete(5) removes the root (two children), delete(42) is not in the tree, 7 (the successor) is still there.")
    assert (t.inorder(), len(t), t.height()) == ([1, 2, 3, 4, 7, 8, 9], 7, 4), (
        "after deleting 5: the keys 1, 2, 3, 4, 7, 8, 9, 7 keys, height 4 (7 - 3 - 1 - 2).")


def test_the_three_delete_cases_and_the_root():
    t = BST()
    for k in (50, 30, 70, 20, 40, 60, 80, 65):
        t.insert(k)
    assert t.delete(20) and t.inorder() == [30, 40, 50, 60, 65, 70, 80], "a leaf."
    assert t.delete(60) and t.inorder() == [30, 40, 50, 65, 70, 80], "60 has one child (65): the child takes its place."
    assert t.delete(50) and t.inorder() == [30, 40, 65, 70, 80], "the root with two children: the successor 65 is the new root key."
    assert t.delete(30) and t.delete(40) and t.delete(65) and t.delete(70) and t.delete(80), "delete the rest."
    assert len(t) == 0 and t.inorder() == [] and t.height() == 0, "after the last delete the tree is empty again."
    assert t.insert(9) is True and t.inorder() == [9] and len(t) == 1, "an emptied tree must accept new keys."


def test_height_counts_nodes():
    t = BST()
    for k in (2, 1, 3):
        t.insert(k)
    assert t.height() == 2, "a root with two leaves has height 2 (nodes)."
    t = BST()
    for k in (1, 2, 3, 4, 5):
        t.insert(k)
    assert t.height() == 5, "sorted keys make a chain: height 5."
    t = BST()
    t.insert(7)
    assert t.height() == 1, "a single key has height 1."


def test_zero_and_negative_keys():
    t = BST()
    for k in (0, -5, 5, -10, 0):
        t.insert(k)
    assert t.inorder() == [-10, -5, 0, 5] and len(t) == 4, "0 and negative numbers are keys (and 0 was inserted twice)."
    assert t.contains(0) and t.contains(-10) and not t.contains(-1), "contains must work for 0 and for negative keys."


def test_inorder_returns_a_new_list():
    t = BST()
    for k in (3, 1, 2):
        t.insert(k)
    a = t.inorder()
    a.append(99)
    a.sort(reverse=True)
    assert t.inorder() == [1, 2, 3], "inorder() must return a new list: changing it must not change the tree."


def test_random_operations_against_a_set():
    rng = random.Random(60)
    t, model = BST(), set()
    for step in range(4000):
        key = rng.randint(0, 60)
        op = rng.choice(["insert", "insert", "delete", "contains"])
        if op == "insert":
            got = t.insert(key)
            want = key not in model
            model.add(key)
            assert got is want, f"step {step}: insert({key}) should return {want}."
        elif op == "delete":
            got = t.delete(key)
            want = key in model
            model.discard(key)
            assert got is want, f"step {step}: delete({key}) should return {want}."
        else:
            assert t.contains(key) is (key in model), f"step {step}: contains({key}) should be {key in model}."
        assert len(t) == len(model), f"step {step}: len should be {len(model)}, got {len(t)}."
        if step % 25 == 0:
            assert t.inorder() == sorted(model), (
                f"step {step}: inorder() should be {sorted(model)}, got {t.inorder()}. "
                "A subtree was lost, or a key stayed in the tree after delete.")
            n = len(model)
            assert t.height() >= n.bit_length() and t.height() <= max(n, 0), "the height must be between log n and n."
    assert t.inorder() == sorted(model), "at the end the keys must still match the set."


def fill(t, keys):
    for k in keys:
        t.insert(k)


def test_sorted_insertions_of_2000_keys_need_no_recursion():
    t = BST()
    with_low_recursion_limit(fill, t, range(2000))
    assert len(t) == 2000, "2,000 sorted insertions: the tree must hold 2,000 keys."
    assert with_low_recursion_limit(t.height) == 2000, "sorted keys make a chain: the height is 2,000."
    assert with_low_recursion_limit(t.inorder) == list(range(2000)), "inorder must give 0..1999."
    assert with_low_recursion_limit(t.contains, 1999) is True and with_low_recursion_limit(t.contains, 2000) is False, (
        "contains must walk down the chain with a loop.")


def test_descending_insertions_and_deleting_a_chain_in_every_order():
    for order in ("ascending", "descending", "middle out"):
        t = BST()
        with_low_recursion_limit(fill, t, range(1999, -1, -1))             # a left chain
        keys = list(range(2000))
        if order == "descending":
            keys.reverse()
        elif order == "middle out":
            keys = sorted(keys, key=lambda k: abs(k - 1000))
        removed = []
        for k in keys[:700]:
            assert with_low_recursion_limit(t.delete, k) is True, f"{order}: delete({k}) must return True."
            removed.append(k)
        gone = set(removed)
        assert len(t) == 1300, f"{order}: after 700 deletes the tree must hold 1,300 keys, got {len(t)}."
        assert with_low_recursion_limit(t.inorder) == [k for k in range(2000) if k not in gone], (
            f"{order}: the 1,300 remaining keys must be in order.")


def test_the_same_keys_in_a_random_order_give_a_low_tree():
    rng = random.Random(61)
    keys = list(range(2000))
    rng.shuffle(keys)
    t = BST()
    fill(t, keys)
    assert t.inorder() == list(range(2000)), "random order: inorder must be 0..1999."
    assert t.height() < 60, f"a random order of 2,000 keys should give a height of about 25, got {t.height()}."
