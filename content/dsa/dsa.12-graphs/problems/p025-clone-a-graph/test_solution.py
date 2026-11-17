import random
from collections import deque

from solution import Node, clone_graph


def make(n, adjacency, vals=None):
    """Build n nodes; adjacency[i] lists neighbour indices in order."""
    nodes = [Node(vals[i] if vals else i) for i in range(n)]
    for i, nbrs in enumerate(adjacency):
        nodes[i].neighbors = [nodes[j] for j in nbrs]
    return nodes


def reachable(start):
    seen, order, queue = {start}, [start], deque([start])
    while queue:
        u = queue.popleft()
        for v in u.neighbors:
            if v not in seen:
                seen.add(v)
                order.append(v)
                queue.append(v)
    return order


def snapshot(start):
    """The shape of the graph as index lists (BFS numbering) plus values."""
    order = reachable(start)
    index = {node: i for i, node in enumerate(order)}
    return [(node.val, [index[v] for v in node.neighbors]) for node in order]


def check_copy(start, label):
    before = snapshot(start)
    old_nodes = reachable(start)
    old_ids = {id(x) for x in old_nodes}
    copy = clone_graph(start)
    assert copy is not None, f"{label}: clone_graph returned None for a real node."
    new_nodes = reachable(copy)
    for x in new_nodes:
        assert id(x) not in old_ids, (
            f"{label}: the copy contains an OLD node (val {x.val}). Every reachable node needs a brand new Node, "
            "and every neighbour list must point to new nodes, not to the original ones.")
        assert x.neighbors is not None
    assert len(new_nodes) == len(old_nodes), (
        f"{label}: the original has {len(old_nodes)} reachable nodes, the copy has {len(new_nodes)}. "
        "One copy per node: look a node up in a dictionary keyed by the node object (not by its value).")
    assert snapshot(copy) == before, (
        f"{label}: the copy does not have the same shape (values and neighbour order). Keep every neighbour entry, "
        "in the original order, including self loops and repeated neighbours.")
    assert snapshot(start) == before, f"{label}: the original graph was changed. Only read it."
    return copy


def test_none():
    crashed = False
    try:
        result = clone_graph(None)
    except AttributeError:
        crashed = True
    assert not crashed, "clone_graph(None) crashed: check `if node is None: return None` first."
    assert result is None, "clone_graph(None) must return None."


def test_single_node():
    a = Node(5)
    c = check_copy(a, "one node")
    assert c.val == 5 and c.neighbors == [], "A single node copies to a single node with an empty list."


def test_triangle_example():
    a, b, c = make(3, [[1, 2], [0, 2], [0, 1]], vals=[1, 2, 3])
    a2 = check_copy(a, "triangle")
    assert a2.neighbors[0].neighbors[0] is a2, (
        "triangle: the copy of b must point back to the SAME copy of a (reuse the copy you already made).")


def test_self_loop_and_repeated_neighbour():
    a, b = make(2, [[1, 1, 0], [0]], vals=[1, 2])
    a2 = check_copy(a, "self loop and [b, b, a]")
    assert a2.neighbors[2] is a2, "A self loop must point to the copy itself."
    assert a2.neighbors[0] is a2.neighbors[1], "A neighbour listed twice is the same copy twice."


def test_equal_values_are_different_nodes():
    a, b, c, d = make(4, [[1, 2], [3], [3], []], vals=[7, 7, 7, 7])
    check_copy(a, "four nodes all with val 7")


def test_only_reachable_part():
    nodes = make(4, [[1], [0], [3], [2]])
    c = check_copy(nodes[0], "two separate pairs")
    assert len(reachable(c)) == 2, "Only the nodes reachable from the given node are copied."


def test_random_graphs():
    rng = random.Random(25)
    for t in range(150):
        n = rng.randint(1, 12)
        adjacency = [[rng.randrange(n) for _ in range(rng.randint(0, 4))] for _ in range(n)]
        nodes = make(n, adjacency, vals=[rng.randint(0, 3) for _ in range(n)])
        check_copy(nodes[rng.randrange(n)], f"random graph #{t}")


def test_long_chain_needs_no_recursion():
    n = 20000
    nodes = make(n, [[i + 1] if i + 1 < n else [0] for i in range(n)])
    crashed = False
    try:
        copy = clone_graph(nodes[0])
    except RecursionError:
        crashed = True
    assert not crashed, (
        "RecursionError on a cycle of 20,000 nodes: use an iterative DFS or a BFS with a queue, "
        "not one recursive call per node.")
    count, x = 0, copy
    while True:
        count += 1
        x = x.neighbors[0]
        if x is copy:
            break
        assert count <= n, "The copied chain does not come back to the start."
    assert count == n, f"The copy of the 20,000-node cycle has {count} nodes."
