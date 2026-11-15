import pytest

from solution import ListNode, length, get


def build(values):
    """Make a chain of ListNode from a Python list and return its head (None if empty)."""
    dummy = ListNode(0)
    tail = dummy
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next


def nodes(head, limit=10**6):
    """The nodes of a chain, in order. A cycle stops the walk with a message instead of hanging."""
    out, seen = [], set()
    cur = head
    while cur is not None:
        if id(cur) in seen:
            raise AssertionError(
                f"your list has a cycle: after {len(out)} nodes the walk reached the node with value {cur.val!r} "
                "again. Some next pointer points back into the list; did the last node keep an old next "
                "instead of None?")
        if len(out) >= limit:
            raise AssertionError(f"your list has more than {limit:,} nodes: the tests never build lists that long.")
        seen.add(id(cur))
        out.append(cur)
        cur = cur.next
    return out


def to_list(head):
    return [n.val for n in nodes(head)]


def check_same_nodes(before, head, what):
    """Nothing lost, nothing new: the chain at head holds exactly the node objects in `before`."""
    after = nodes(head)
    had = {id(n) for n in before}
    has = {id(n) for n in after}
    lost = [n.val for n in before if id(n) not in has]
    new = [n.val for n in after if id(n) not in had]
    assert not lost, (f"{what}: nodes with values {lost[:6]} were lost. A next pointer was overwritten "
                      "before its old value was saved in a variable.")
    assert not new, (f"{what}: the result contains new nodes (values {new[:6]}). Rewire the existing "
                     "nodes instead of creating new ones.")


@pytest.mark.parametrize("values", [[], [7], [1, 2], [0, 0, 0], list(range(10))])
def test_length(values):
    head = build(values)
    got = length(head)
    assert got == len(values), (
        f"length of a chain with {len(values)} nodes should be {len(values)}, got {got}. "
        "Count every node, including the first and the last; the empty chain (None) has length 0.")
    assert to_list(head) == values, "length must not change the chain."


def test_length_counts_falsy_values():
    assert length(build([0, None, ""])) == 3, "Stop at a None NODE, not at a falsy VALUE: 0, None and '' are values."


def test_length_long():
    assert length(build(range(10**5))) == 10**5, "A chain of 100,000 nodes: use a loop, not recursion."


def test_get_returns_the_node():
    head = build([10, 20, 30])
    ns = nodes(head)
    for k in range(3):
        got = get(head, k)
        assert got is ns[k], (
            f"get(head, {k}) should return the node object holding {ns[k].val} (the same object, not its "
            f"value and not a copy), got {got!r}. Take exactly k steps: index 0 is the head.")


@pytest.mark.parametrize("values, k", [([10, 20, 30], 3), ([10, 20, 30], 10), ([], 0), ([5], 1)])
def test_get_out_of_range(values, k):
    try:
        got = get(build(values), k)
    except AttributeError:
        raise AssertionError(
            f"get on a list of length {len(values)} with k={k} crashed with AttributeError: you stepped past "
            "the last node and asked None for .next. Check for None before each step.") from None
    assert got is None, f"There is no index {k} in a list of length {len(values)}: return None, got {got!r}."


def test_get_negative():
    assert get(build([1, 2, 3]), -1) is None, "A negative k is out of range here: return None."


def test_get_does_not_change_the_chain():
    head = build([1, 2, 3, 4])
    get(head, 2)
    get(head, 9)
    assert to_list(head) == [1, 2, 3, 4], "get must only walk, never relink."
