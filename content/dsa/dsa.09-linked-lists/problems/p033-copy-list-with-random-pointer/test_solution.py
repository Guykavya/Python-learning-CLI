import random as rnd

import pytest

from solution import RNode, copy_random_list


def make(pairs):
    ns = [RNode(v) for v, _ in pairs]
    for i, (_, r) in enumerate(pairs):
        if i + 1 < len(ns):
            ns[i].next = ns[i + 1]
        ns[i].random = ns[r] if r is not None else None
    return (ns[0] if ns else None), ns


def walk(head, limit=10**5):
    out, seen = [], set()
    while head is not None:
        assert id(head) not in seen and len(out) < limit, "your list has a cycle: a next pointer leads back."
        seen.add(id(head))
        out.append(head)
        head = head.next
    return out


def shape(head):
    ns = walk(head)
    index = {id(n): i for i, n in enumerate(ns)}
    out = []
    for n in ns:
        if n.random is None:
            out.append([n.val, None])
        else:
            assert id(n.random) in index, (
                f"The copy of the node with value {n.val!r} has a random pointer to a node that is not in the copy. "
                "Point randoms at COPIES (the original's random target -> its copy), never into the original list.")
            out.append([n.val, index[id(n.random)]])
    return out


EXAMPLES = [
    [[7, None], [13, 0], [11, 4], [10, 2], [1, 0]],
    [[1, 1], [2, 1]],
    [[3, None], [3, 0], [3, None]],
    [[5, 0]],
    [[5, None]],
]


@pytest.mark.parametrize("pairs", EXAMPLES)
def test_examples(pairs):
    head, ns = make(pairs)
    links = [(n.next, n.random) for n in ns]
    got = copy_random_list(head)
    after = [(n.next, n.random) for n in ns]
    assert all(a is c and b is d for (a, b), (c, d) in zip(links, after)), (
        "The original list was changed. If you interleave copies into it, separate the lists again and restore "
        "every original next pointer.")
    copy_nodes = walk(got)
    shared = {id(n) for n in ns} & {id(n) for n in copy_nodes}
    assert not shared, "The copy shares nodes with the original. A deep copy creates a NEW node for every node."
    assert shape(got) == pairs, (
        f"The copy should have the shape {pairs} ([value, index of random]), got {shape(got)}.")


def test_empty():
    assert copy_random_list(None) is None, "The copy of an empty list is None."


def test_random_lists():
    g = rnd.Random(33)
    for _ in range(200):
        n = g.randint(1, 15)
        pairs = [[g.randint(0, 3), g.choice([None] + list(range(n)))] for _ in range(n)]
        head, ns = make(pairs)
        got = copy_random_list(head)
        assert shape(got) == pairs, f"Wrong copy for {pairs}: got {shape(got)}."
        assert shape(head) == pairs, f"The original {pairs} was changed to {shape(head)}."
        assert not ({id(x) for x in ns} & {id(x) for x in walk(got)}), "The copy shares nodes with the original."


def test_long():
    n = 10**4
    pairs = [[i, (i * 7919) % n] for i in range(n)]
    head, _ = make(pairs)
    got = copy_random_list(head)
    assert shape(got) == pairs, "A list of 10,000 nodes with random pointers everywhere."
