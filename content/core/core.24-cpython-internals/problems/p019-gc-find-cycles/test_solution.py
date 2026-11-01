import gc

from solution import cycle_path, in_cycle


class Node:
    def __init__(self, value=None):
        self.value = value
        self.next = None


class Button:
    def __init__(self):
        self.handler = self.on_click     # a bound method that holds self: an accidental cycle

    def on_click(self):
        return "clicked"


KEEP = Node("global")   # reachable from this module's globals, but NOT in a cycle of its own


def assert_real_path(path, obj):
    assert path is not None, "Expected a path, got None."
    assert path[0] is obj and path[-1] is obj, "The path must start and end with the object itself (`is`)."
    for a, b in zip(path, path[1:]):
        assert any(r is b for r in gc.get_referents(a)), (
            f"Step {type(a).__name__} -> {type(b).__name__} is not a referent link: each item must be in "
            "gc.get_referents(previous item)."
        )


def test_self_referencing_list():
    lst = []
    lst.append(lst)
    assert in_cycle(lst), "lst contains itself: a 1-step cycle."
    path = cycle_path(lst)
    assert path is not None and len(path) == 2 and path[0] is lst and path[1] is lst, (
        "A list that contains itself has the path [lst, lst]."
    )


def test_two_lists():
    a, b = [], []
    a.append(b)
    b.append(a)
    path = cycle_path(a)
    assert path is not None and [id(x) for x in path] == [id(a), id(b), id(a)], (
        "a -> b -> a: return the objects themselves, starting and ending with a."
    )


def test_no_cycle():
    a, b = [], [1, "x"]
    a.append(b)
    assert not in_cycle(a) and cycle_path(a) is None, "a -> b and b holds only an int and a str: no cycle."
    assert not in_cycle(42) and not in_cycle("text"), "Atoms refer to nothing."


def test_dict_cycle():
    d = {}
    d["me"] = d
    assert in_cycle(d), "A dict that is its own value is a cycle (dict referents are its keys and values)."


def test_cycle_through_tuple_and_list():
    holder = []
    t = (1, holder)
    holder.append(t)
    assert in_cycle(t) and in_cycle(holder)


def test_instances_in_a_cycle():
    a, b = Node("a"), Node("b")
    a.next = b
    b.next = a
    assert in_cycle(a) and in_cycle(b), "a.next = b and b.next = a form a cycle."
    assert_real_path(cycle_path(a), a)


def test_pointing_into_a_cycle_is_not_being_in_it():
    x, y, z = Node(), Node(), Node()
    x.next = y
    y.next = z
    z.next = y
    assert in_cycle(y) and in_cycle(z), "y and z point at each other."
    assert not in_cycle(x), (
        "x only points INTO the y/z cycle; nothing leads back to x. Only arriving at the START object counts, "
        "not finding any cycle."
    )


def test_bound_method_cycle():
    button = Button()
    assert in_cycle(button), "self.handler = self.on_click: the bound method refers back to the object."
    assert_real_path(cycle_path(button), button)


def test_class_and_globals_are_not_followed():
    assert not in_cycle(KEEP), (
        "KEEP is a module global. Its class leads to __init__, whose __globals__ contain KEEP, but that is "
        "not a cycle of the object. Do not follow into classes, modules or functions."
    )


def test_shortest_path():
    target = []
    middle = [target]
    long_way = [[[middle]]]
    target.append(long_way)
    target.append(middle)
    path = cycle_path(target)
    assert path is not None and [id(x) for x in path] == [id(target), id(middle), id(target)], (
        "Two ways lead back: target -> middle -> target (2 steps) and a longer one. Breadth-first search "
        "returns the shortest."
    )


def test_depth_limit_boundary():
    start = []
    node = start
    for _ in range(99):            # 100 lists in a ring: start -> l1 -> ... -> l99 -> start
        nxt = []
        node.append(nxt)
        node = nxt
    node.append(start)
    assert in_cycle(start, max_depth=100), "The ring is 100 steps long, so max_depth=100 must find it."
    assert not in_cycle(start, max_depth=99), "With max_depth=99 the ring (100 steps) is too long."
    assert len(cycle_path(start, max_depth=100)) == 101, "A 100-step path lists 101 objects (start twice)."


def test_breadth_first_beats_visited_trap():
    # Both orders are tried, so a depth-first search fails whichever referent it explores first.
    for order in ("a first", "b first"):
        c, b, a = [], [], []
        obj = [a, b] if order == "a first" else [b, a]
        a.append(b)            # obj -> a -> b -> c -> obj is 4 steps
        b.append(c)            # obj -> b -> c -> obj is 3 steps
        c.append(obj)
        assert in_cycle(obj, max_depth=3), (
            f"({order}) obj -> b -> c -> obj is 3 steps. A depth-first search that first reaches b via a "
            "(at step 2) marks it visited and never tries the shorter route. Search breadth-first."
        )
        path = cycle_path(obj, max_depth=3)
        assert [id(x) for x in path] == [id(obj), id(b), id(c), id(obj)], f"({order}) Return the 3-step path."


def test_other_cycles_do_not_hang():
    loop = []
    loop.append(loop)
    start = [loop, [loop]]
    assert not in_cycle(start), "start points into another cycle; visiting each object once keeps this finite."
