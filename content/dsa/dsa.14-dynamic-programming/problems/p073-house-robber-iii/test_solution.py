import pathlib
import random
import subprocess
import sys
from collections import deque

from solution import rob_tree

HERE = pathlib.Path(__file__).parent


class Node:
    """The tests' own tree node, with the same fields as TreeNode."""
    def __init__(self, val, left=None, right=None):
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


def brute(root):
    """Every set of nodes, keeping only sets with no parent-child pair."""
    nodes, links = [], []
    stack = [(root, None)]
    while stack:
        node, parent = stack.pop()
        if node is None:
            continue
        idx = len(nodes)
        nodes.append(node.val)
        if parent is not None:
            links.append((parent, idx))
        stack.append((node.left, idx))
        stack.append((node.right, idx))
    best = 0
    for mask in range(1 << len(nodes)):
        if all(not (mask >> a & 1 and mask >> b & 1) for a, b in links):
            best = max(best, sum(nodes[i] for i in range(len(nodes)) if mask >> i & 1))
    return best


def random_tree(rng, size):
    nodes = [Node(rng.randint(0, 10))]
    while len(nodes) < size:
        parent = rng.choice(nodes)
        child = Node(rng.randint(0, 10))
        if parent.left is None and rng.random() < 0.5:
            parent.left = child
        elif parent.right is None:
            parent.right = child
        else:
            continue
        nodes.append(child)
    return nodes[0]


def test_chapter_examples():
    assert rob_tree(build([3, 2, 3, None, 3, None, 1])) == 7, "Expected 7: rob the root 3 and the grandchildren 3 and 1."
    assert rob_tree(build([3, 4, 5, 1, 3, None, 1])) == 9, "Expected 9: rob 4 and 5."


def test_skip_does_not_mean_rob_children():
    assert rob_tree(build([2, 1, 3, None, 4])) == 7, (
        "Expected 7: rob 4 and 3. Node 1 is skipped AND its parent 2 is skipped. When a node is skipped, each "
        "child is free: skip = max(lrob, lskip) + max(rrob, rskip).")


def test_mixed_levels():
    assert rob_tree(build([4, 1, None, 2, None, 3])) == 7, (
        "Expected 7 (rob 4 and 3, levels 0 and 3). Summing every other level is not enough.")


def test_empty_and_single():
    assert rob_tree(None) == 0, "No houses: 0."
    assert rob_tree(Node(5)) == 5, "One house: rob it."


def test_random_against_brute():
    rng = random.Random(73)
    for _ in range(300):
        root = random_tree(rng, rng.randint(1, 12))
        want = brute(root)
        got = rob_tree(root)
        assert got == want, (
            f"Expected {want} (every allowed set of houses tried), got {got}. Return (rob, skip) from each "
            "node: rob = val + lskip + rskip, skip = max(lrob, lskip) + max(rrob, rskip).")


def test_large_trees_in_time():
    code = (
        "import random\n"
        "from solution import rob_tree\n"
        "class Node:\n"
        "    def __init__(self, val, left=None, right=None):\n"
        "        self.val, self.left, self.right = val, left, right\n"
        "rng = random.Random(7300)\n"
        "level = [Node(rng.randint(0, 10**4)) for _ in range(2**16)]\n"
        "while len(level) > 1:\n"
        "    level = [Node(rng.randint(0, 10**4), level[k], level[k + 1]) for k in range(0, len(level), 2)]\n"
        "print(rob_tree(level[0]))\n"
        "chain = None\n"
        "for k in range(700):\n"
        "    chain = Node(rng.randint(0, 10**4), chain, None)\n"
        "print(rob_tree(chain))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=15, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (15 s) on a perfect tree of 131,071 nodes and a chain of 700. Recursing to the grandchildren "
        "without a memo solves each subtree again and again (exponential on the chain): return the pair "
        "(rob, skip) from every node instead.")
    assert r.returncode == 0, "Your code crashed on the large trees:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["442665165", "2017691"], (
        f"Expected 442665165 for the perfect tree and 2017691 for the chain; got {r.stdout.split()}.")
