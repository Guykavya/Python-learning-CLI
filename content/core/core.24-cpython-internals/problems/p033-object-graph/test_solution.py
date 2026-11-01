import json

from solution import reachable, summary


class Node:
    registry = ["class attributes", "are not", "part of an instance"]

    def __init__(self, value=None, next=None):
        self.value = value
        self.next = next


class Slotted:
    __slots__ = ("a", "b")

    def __init__(self, a, b):
        self.a = a
        self.b = b


def chain(n):
    head = None
    for i in reversed(range(n)):
        head = Node(i, head)
    return head


def ids(objects):
    return {id(o) for o in objects}


def test_linked_list():
    head = chain(5)
    found = reachable(head)
    assert found[0] is head, "The root comes first."
    assert summary(head) == {"Node": 5}, "Follow each node's attributes: 5 nodes are reachable from the head."


def test_cycle_terminates():
    a, b = Node("a"), Node("b")
    a.next, b.next = b, a
    assert summary(a) == {"Node": 2}, "Remember what you have seen (by id) so a cycle is visited once."


def test_containers_are_counted():
    root = Node([1, (2, 3), {4, 5}, frozenset({6})])
    assert summary(root) == {"Node": 1, "list": 1, "tuple": 1, "set": 1, "frozenset": 1}, (
        "list, tuple, set and frozenset are containers: count them and follow what they hold."
    )


def test_dicts_are_followed_but_not_counted():
    target = Node("deep")
    root = {"a": [1, 2], "b": {"c": target}}
    found = reachable(root)
    assert summary(root) == {"list": 1, "Node": 1}, (
        "Plain dicts are walked through (their values are followed) but never counted, not even the root."
    )
    assert id(target) in ids(found), "An object inside a dict inside a dict is reachable."


def test_same_result_with_or_without_instance_dict():
    head = chain(3)
    head.extra = [1, 2]
    before = summary(head)
    for node in reachable(head):
        if isinstance(node, Node):
            vars(node)  # on newer Pythons this creates a real __dict__ object for the instance
    after = summary(head)
    assert before == after == {"Node": 3, "list": 1}, (
        "Whether gc.get_referents(instance) reports an instance __dict__ or the attribute values directly is a "
        "CPython detail that changed in 3.11-3.13. Treat dicts as transparent so both give the same summary."
    )


def test_shared_objects_counted_once():
    x = [1]
    root = [x, x, (x,)]
    assert summary(root) == {"list": 2, "tuple": 1}, "x is reachable three ways but is ONE object: count it once."


def test_class_function_module_not_followed():
    root = Node(json, Node(len, Node(print)))
    root.callback = test_cycle_terminates
    root.kind = Node
    assert summary(root) == {"Node": 3}, (
        "Do not follow types (the class, reached from every instance), functions, builtins or modules: they "
        "lead to the whole program. Node.registry is a class attribute and must not be counted."
    )


def test_atoms_not_counted():
    root = Node("text", Node(42, Node(3.5, Node(None, Node(True)))))
    assert summary(root) == {"Node": 5}, "Strings, numbers, None and bools are not containers or user objects."


def test_slots_objects():
    inner = [1, 2]
    root = Slotted(inner, Slotted((3,), None))
    assert summary(root) == {"Slotted": 2, "list": 1, "tuple": 1}, (
        "An object with __slots__ has no __dict__; gc.get_referents returns its slot values directly."
    )


def test_max_nodes_truncates_breadth_first():
    head = chain(100)
    found = reachable(head, max_nodes=10)
    assert len(found) == 10, "Stop once max_nodes objects have been found."
    expected, node = [], head
    for _ in range(10):
        expected.append(node)
        node = node.next
    assert [id(o) for o in found] == [id(o) for o in expected], "Walk breadth-first from the root: the first 10 nodes."
    assert summary(head, max_nodes=10) == {"Node": 10}, "summary passes max_nodes on to reachable."


def test_long_chain_no_recursion_error():
    head = chain(5_000)
    assert summary(head) == {"Node": 5_000}, (
        "Use a queue (or an explicit stack), not recursion: a 5,000-node chain would hit the recursion limit."
    )


def test_root_that_is_not_interesting():
    assert reachable(42) == [] and summary("text") == {}, "An int or a string root reaches nothing."


def test_tree():
    leaves = [Node(i) for i in range(4)]
    left, right = Node(leaves[:2]), Node(leaves[2:])
    root = Node((left, right))
    assert summary(root) == {"Node": 7, "list": 2, "tuple": 1}, "1 root + 2 inner + 4 leaves, 2 lists, 1 tuple."
    assert ids(leaves) <= ids(reachable(root)), "Every leaf is reachable."
