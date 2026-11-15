import pytest

from solution import ListNode, from_list, to_list


def walk(head, limit=10**5 + 5):
    """The test's own walker: the values of a chain, with a step limit so a cycle cannot hang."""
    out, cur = [], head
    while cur is not None:
        assert len(out) < limit, "your list has a cycle: the walk never reached a node whose next is None."
        out.append(cur.val)
        cur = cur.next
    return out


def chain(*values):
    head = None
    for v in reversed(values):
        head = ListNode(v, head)
    return head


@pytest.mark.parametrize("values", [[1], [1, 2, 3], [5, 5, 5], ["a", "b"], [0, None, False, ""]])
def test_from_list_values(values):
    head = from_list(values)
    assert isinstance(head, ListNode), f"from_list({values!r}) should return the first ListNode, got {head!r}."
    assert walk(head) == values, (
        f"from_list({values!r}) built a chain holding {walk(head)!r}. Each new node must be linked "
        "after the previous one (move the tail forward after linking).")


def test_from_list_empty_is_none():
    assert from_list([]) is None, (
        "An empty list has no first node, so from_list([]) must return None, not a node with val 0 "
        "(did you return the dummy instead of dummy.next?).")


def test_from_list_returns_first_node_not_dummy():
    head = from_list([7, 8])
    assert head.val == 7, (
        f"The head should hold 7, got {head.val!r}. If it is 0, you returned the dummy node itself; return dummy.next.")


def test_last_node_points_to_none():
    head = from_list([1, 2, 3])
    assert head.next.next.next is None, "The last node's next must be None: that is how a walk knows it has ended."


def test_from_list_makes_new_nodes():
    a = from_list([1, 2])
    b = from_list([1, 2])
    assert a is not b and a.next is not b.next, "Every call to from_list must create new nodes."


def test_to_list():
    assert to_list(chain(4, 5, 6)) == [4, 5, 6], "to_list should give the values from the head to the end, in order."
    assert to_list(None) == [], "to_list(None) is the empty list: there are no nodes to visit."
    assert to_list(chain(9)) == [9], "A single node gives a list with one value."


def test_to_list_keeps_falsy_values():
    assert to_list(chain(0, None, "", 3)) == [0, None, "", 3], (
        "Values 0, None and '' are real values. Stop when the NODE is None (while cur is not None), "
        "not when the value is falsy.")


def test_to_list_does_not_change_the_chain():
    head = chain(1, 2, 3)
    second = head.next
    to_list(head)
    assert head.next is second and walk(head) == [1, 2, 3], "to_list must only read the chain, never relink it."


def test_round_trip_long():
    values = list(range(10**5))
    assert to_list(from_list(values)) == values, (
        "100,000 values must survive the round trip. If this crashed with RecursionError, use loops, not recursion.")
