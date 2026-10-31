import pytest

from solution import SparseList


def test_new_list_is_all_default():
    s = SparseList(4)
    assert len(s) == 4, "len() is the logical size you passed in, even though nothing is stored."
    assert [s[i] for i in range(4)] == [0, 0, 0, 0], "Positions never set read as the default value."
    assert s.stored_count == 0, "A new SparseList stores nothing: stored_count is 0."


def test_custom_default():
    s = SparseList(2, default="-")
    assert s[0] == "-" and s[1] == "-", "default= is returned for positions never set."


def test_setitem_and_getitem():
    s = SparseList(5)
    s[1] = 7
    s[4] = 9
    assert s[1] == 7 and s[4] == 9, "__setitem__ must remember the value so __getitem__ can return it."
    assert s[0] == 0 and s[2] == 0, "Other positions are still the default."
    assert s.stored_count == 2, "stored_count is the number of positions that hold a non-default value."


def test_setting_default_frees_the_slot():
    s = SparseList(3)
    s[1] = 5
    s[1] = 0
    assert s[1] == 0, "Assigning the default value reads back as the default."
    assert s.stored_count == 0, "Assigning the default value should REMOVE the entry: that is what 'sparse' means."


def test_negative_indices():
    s = SparseList(3)
    s[-1] = 8
    assert s[2] == 8 and s[-1] == 8, "Negative indices count from the end, for both reading and writing."
    assert s.stored_count == 1, "s[-1] and s[2] are the same position: store ONE entry keyed by the normalised index."


def test_index_errors():
    s = SparseList(3)
    for bad in (3, -4, 10):
        with pytest.raises(IndexError):
            s[bad]
        with pytest.raises(IndexError):
            s[bad] = 1
        with pytest.raises(IndexError):
            del s[bad]
    with pytest.raises(TypeError):
        s["a"]
    assert len(s) == 3, "Failed operations must not change the size."


def test_delitem_shifts_left():
    s = SparseList(5)
    s[0], s[2], s[4] = "a", "b", "c"
    del s[1]
    assert len(s) == 4, "del s[i] removes a position, so len() goes down by one (like a list)."
    assert [s[i] for i in range(4)] == ["a", "b", 0, "c"], "Items after the deleted index move one place left: keys greater than the deleted index must decrease by 1."


def test_delitem_of_stored_item():
    s = SparseList(4)
    s[1], s[3] = "x", "y"
    del s[1]
    assert list(s) == [0, 0, "y"], "Deleting a stored position removes its value and shifts the later ones left."
    assert s.stored_count == 1, "The deleted entry must leave the storage, and only 'y' remains."
    del s[-1]
    assert list(s) == [0, 0] and s.stored_count == 0, "Negative index in __delitem__ works too."


def test_iteration_and_free_container_features():
    s = SparseList(4, default=None)
    s[2] = "z"
    assert list(s) == [None, None, "z", None], "__iter__ yields every logical position including defaults."
    assert "z" in s and None in s, "`in` should work through __iter__ (or __getitem__)."
    assert len(list(s)) == len(s), "Iteration must be exactly len(s) long."


def test_huge_list_is_cheap():
    s = SparseList(10**9)
    s[5] = 1
    s[10**9 - 1] = 2
    assert len(s) == 10**9 and s.stored_count == 2, "Never build a real list of `size` items: store only non-default positions in a dict."
    assert s[-1] == 2, "Reading a far position must be O(1)."


def test_repr():
    s = SparseList(3)
    s[1] = 4
    assert repr(s) == "SparseList([0, 4, 0], default=0)", "repr shows the whole logical list and the default: SparseList([0, 4, 0], default=0)."
