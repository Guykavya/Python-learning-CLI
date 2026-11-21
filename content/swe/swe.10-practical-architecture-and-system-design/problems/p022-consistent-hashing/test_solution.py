import hashlib
from collections import Counter

import pytest

from solution import Ring

KEYS = [f"user:{i}" for i in range(10_000)]


def md5_position(text):
    return int(hashlib.md5(text.encode()).hexdigest(), 16)


def owners(ring):
    return {k: ring.node_for(k) for k in KEYS}


def moved(a, b):
    return sum(a[k] != b[k] for k in KEYS) / len(KEYS)


def test_the_mapping_is_the_same_in_every_process():
    ring = Ring(["A", "B", "C"])
    assert [ring.node_for(k) for k in ("user:1", "user:2", "user:3", "order:77", "a", "")] == ["A", "C", "C", "B", "B", "A"], \
        "Positions must come from hashlib.md5 (int of the hex digest) and the points from f'{node}#{i}': hash() is randomised per process and would disagree between servers."


def test_a_key_always_goes_to_the_same_node():
    ring = Ring(["A", "B", "C"])
    assert all(ring.node_for("user:42") == ring.node_for("user:42") for _ in range(5))


def test_adding_a_fifth_node_moves_about_a_fifth_of_the_keys():
    before, after = owners(Ring(list("ABCD"))), owners(Ring(list("ABCDE")))
    fraction = moved(before, after)
    assert 0.12 <= fraction <= 0.30, f"A ring should move only the new node's share (about 20%); {fraction:.1%} of the keys moved."
    assert all(after[k] == "E" for k in KEYS if before[k] != after[k]), "Keys may only move TO the new node, never between old nodes."


def test_modulo_moves_most_keys_for_contrast():
    nodes4, nodes5 = list("ABCD"), list("ABCDE")
    fraction = sum(nodes4[md5_position(k) % 4] != nodes5[md5_position(k) % 5] for k in KEYS) / len(KEYS)
    assert 0.70 <= fraction <= 0.90, f"hash % N moves about 80% of the keys when N goes from 4 to 5 (measured here: {fraction:.1%}): that is why the ring exists."


def test_virtual_nodes_make_the_shares_even():
    share = Counter(owners(Ring(list("ABCD"), vnodes=100)).values())
    assert all(1_800 <= n <= 3_200 for n in share.values()), f"With 100 virtual points each, four nodes should hold about 2,500 of 10,000 keys each; got {dict(share)}"


def test_one_point_per_node_is_lumpy():
    share = Counter(owners(Ring(list("ABCD"), vnodes=1)).values())
    assert max(share.values()) - min(share.values()) > 2_500 or len(share) < 4, "With one point per node the split is very uneven (the chapter measured 640 / 272 / 8,034 / 11,054)."


def test_the_order_of_adding_does_not_matter():
    assert owners(Ring(list("ABCD"))) == owners(Ring(list("DCBA"))), "The ring depends only on the SET of nodes."
    ring = Ring()
    for node in "CABD":
        ring.add(node)
    assert owners(ring) == owners(Ring(list("ABCD")))


def test_remove_puts_the_keys_back():
    ring = Ring(list("ABCD"))
    ring.remove("D")
    assert owners(ring) == owners(Ring(list("ABC"))), "After removing D the ring must equal a ring built without D."


def test_remove_moves_only_the_keys_of_the_removed_node():
    ring = Ring(list("ABCD"))
    before = owners(ring)
    ring.remove("B")
    after = owners(ring)
    assert all(before[k] == after[k] for k in KEYS if before[k] != "B"), "Keys of the nodes that stay must not move."
    assert all(after[k] != "B" for k in KEYS)


def test_add_and_remove_are_inverses():
    ring = Ring(list("ABC"))
    before = owners(ring)
    ring.add("D")
    ring.remove("D")
    assert owners(ring) == before


def test_errors():
    ring = Ring(["A"])
    with pytest.raises(ValueError):
        ring.add("A")
    with pytest.raises(KeyError):
        ring.remove("Z")
    with pytest.raises(ValueError, match="empty"):
        Ring().node_for("user:1")
    ring.remove("A")
    with pytest.raises(ValueError):
        ring.node_for("user:1")


def test_a_single_node_owns_everything():
    ring = Ring(["only"])
    assert {ring.node_for(k) for k in KEYS[:500]} == {"only"}


def test_wrap_around():
    ring = Ring(["A", "B"], vnodes=1)
    last_position = ring.points[-1][0]
    key = next(k for k in (f"probe:{i}" for i in range(10_000)) if md5_position(k) > last_position)
    assert ring.node_for(key) == ring.points[0][1], "A key beyond the last point wraps around to the FIRST point of the circle."


def test_vnodes_parameter_changes_the_number_of_points():
    assert len(Ring(["A", "B"], vnodes=7).points) == 14, "Each node puts `vnodes` points on the ring (the tests look at `ring.points`, a sorted list of (position, node))."
