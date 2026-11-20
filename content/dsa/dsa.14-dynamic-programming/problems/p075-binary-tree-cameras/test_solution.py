import pathlib
import random
import subprocess
import sys
from collections import deque

from solution import min_cameras

HERE = pathlib.Path(__file__).parent


class Node:
    """The tests' own tree node, with the same fields as TreeNode."""
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build(values):
    if not values or values[0] is None:
        return None
    root = Node(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values) and values[i] is not None:
            node.left = Node(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = Node(values[i])
            queue.append(node.right)
        i += 1
    return root


def chain(n):
    """A path of n nodes going down, zig-zagging left and right."""
    root = None
    for k in range(n):
        root = Node(0, root, None) if k % 2 else Node(0, None, root)
    return root


def brute(root):
    """Try every set of camera nodes and keep the smallest set that watches every node (small trees only)."""
    nodes, links = [], []
    stack = [(root, None)]
    while stack:
        node, parent = stack.pop()
        if node is None:
            continue
        idx = len(nodes)
        nodes.append(node)
        if parent is not None:
            links.append((parent, idx))
        stack.append((node.left, idx))
        stack.append((node.right, idx))
    n = len(nodes)
    best = n
    for mask in range(1 << n):
        cams = bin(mask).count("1")
        if cams >= best:
            continue
        watched = mask
        for a, b in links:
            if mask >> a & 1:
                watched |= 1 << b
            if mask >> b & 1:
                watched |= 1 << a
        if watched == (1 << n) - 1:
            best = cams
    return best


def random_tree(rng, size):
    nodes = [Node()]
    while len(nodes) < size:
        parent = rng.choice(nodes)
        child = Node()
        if parent.left is None and rng.random() < 0.5:
            parent.left = child
        elif parent.right is None:
            parent.right = child
        else:
            continue
        nodes.append(child)
    return nodes[0]


def test_examples():
    assert min_cameras(build([0, 0, None, 0, 0])) == 1, (
        "Expected 1: a camera on the root's child watches the root, itself and both of its children.")
    got = min_cameras(build([0, 0, None, 0, None, 0, None, None, 0]))
    assert got == 2, (
        f"Chain of 5 nodes A-B-C-D-E: cameras on B and D watch everything, expected 2, got {got}. "
        "If you got 1, you only put cameras on leaves (E): that leaves A and B unwatched.")


def test_empty_and_single():
    assert min_cameras(None) == 0, "No tree: no cameras."
    got = min_cameras(Node())
    assert got == 1, (
        f"A single node needs 1 camera, got {got}. If you got 0: at the ROOT the mode 'not watched yet' is "
        "not allowed, because the root has no parent to watch it. Answer = min(watched, camera).")


def test_leaves_are_bad_places():
    got = min_cameras(chain(3))
    assert got == 1, (
        f"Chain of 3: one camera in the middle watches all three, expected 1, got {got}. A camera on a leaf "
        "watches only 2 nodes; on its parent it watches 3 or more.")
    assert min_cameras(chain(4)) == 2, "Chain of 4: expected 2 (each camera can cover at most 3 nodes of a path)."


def test_full_tree():
    got = min_cameras(build([0] * 7))
    assert got == 2, (
        f"A full tree of 7 nodes: cameras on the two children of the root watch every node, expected 2, got {got}.")
    got = min_cameras(build([0] * 15))
    assert got == 5, (
        f"A full tree of 15 nodes: expected 5 (the 4 parents of leaves, plus the root), got {got}. "
        "A greedy 'camera on every other level' gives more.")


def test_random_against_brute_force():
    rng = random.Random(75)
    for _ in range(250):
        root = random_tree(rng, rng.randint(1, 12))
        want = brute(root)
        got = min_cameras(root)
        assert got == want, (
            f"Expected {want} cameras (every set of camera nodes tried), got {got}. Return three numbers per "
            "node: (not watched yet, watched by a child, has a camera). A missing child returns (0, 0, inf).")


def test_large_trees_in_time():
    code = (
        "from solution import min_cameras\n"
        "class Node:\n"
        "    def __init__(self, val=0, left=None, right=None):\n"
        "        self.val, self.left, self.right = val, left, right\n"
        "level = [Node() for _ in range(2**16)]\n"
        "while len(level) > 1:\n"
        "    level = [Node(0, level[k], level[k + 1]) for k in range(0, len(level), 2)]\n"
        "print(min_cameras(level[0]))\n"
        "chain = None\n"
        "for k in range(700):\n"
        "    chain = Node(0, chain, None) if k % 2 else Node(0, None, chain)\n"
        "print(min_cameras(chain))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=15, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (15 s) on a perfect tree of 131,071 nodes and a chain of 700. Trying 'camera or not' on "
        "every node without returning the three numbers per node is exponential.")
    assert r.returncode == 0, "Your code crashed on the large trees:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["37449", "234"], (
        f"Expected 37449 for the perfect tree and 234 (= ceil(700 / 3)) for the chain; got {r.stdout.split()}.")
