from solution import extra_refs


class Box:
    pass


def test_list_slot():
    assert extra_refs(lambda o: [o]) == 1, (
        "A list holding the object adds 1. If you got 0, you did not keep store()'s return value alive "
        "before the second count."
    )


def test_same_object_three_times():
    assert extra_refs(lambda o: [o, o, o]) == 3, "Each slot is a separate reference, even to the same object."


def test_dict_value_and_key():
    assert extra_refs(lambda o: {"key": o}) == 1, "A dict value is one reference."
    assert extra_refs(lambda o: {o: "value"}) == 1, "A dict key is one reference too."
    assert extra_refs(lambda o: (o, {o: 1})) == 2, "A tuple slot plus a dict key: 2."


def test_attribute():
    def store(o):
        box = Box()
        box.item = o
        return box

    assert extra_refs(store) == 1, "An instance attribute is one reference from the instance's __dict__."


def test_nothing_kept():
    assert extra_refs(lambda o: None) == 0, "store kept nothing, so the count must not change."
    assert extra_refs(lambda o: len([o, o])) == 0, (
        "The temporary list is gone by the time store returns; only what store returns is kept."
    )


def test_uses_a_fresh_ordinary_object():
    seen = []

    def store(o):
        seen.append(o)
        return None

    extra_refs(store)
    extra_refs(store)
    assert type(seen[0]) is object, (
        "Create the object with object(). Numbers, strings and None may be immortal (3.12+) or shared, so deltas lie."
    )
    assert seen[0] is not seen[1], "Make a NEW object on every call, inside extra_refs."


def test_returns_int():
    result = extra_refs(lambda o: [o])
    assert isinstance(result, int), "Return the difference as an int (after - before)."
