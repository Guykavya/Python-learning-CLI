import pytest

from solution import Permission, Priority, allows, describe, highest, parse


def test_flag_members_and_bit_values():
    assert issubclass(Permission, __import__("enum").Flag), "Permission must be an enum.Flag (not a plain Enum), so members can be combined with |."
    assert [Permission.READ.value, Permission.WRITE.value, Permission.EXECUTE.value] == [1, 2, 4], "With auto(), a Flag gets the values 1, 2, 4 (powers of two)."


def test_combining_flags():
    rw = Permission.READ | Permission.WRITE
    assert Permission.READ in rw and Permission.WRITE in rw, "`flag in combo` tests whether the bit is set."
    assert Permission.EXECUTE not in rw, "EXECUTE is not part of READ|WRITE."
    assert rw.value == 3, "READ|WRITE has the value 1 | 2 == 3."
    assert (rw & Permission.WRITE) == Permission.WRITE, "& keeps the common bits."
    assert (rw ^ Permission.WRITE) == Permission.READ, "^ toggles bits."


def test_empty_flag_is_falsy():
    none = Permission(0)
    assert not none and none.value == 0, "Permission(0) is the empty combination, and it is falsy."
    assert Permission.READ, "A non-empty flag is truthy."


def test_describe():
    assert describe(Permission.READ | Permission.WRITE | Permission.EXECUTE) == "rwx", "All three flags give 'rwx'."
    assert describe(Permission.READ | Permission.EXECUTE) == "r-x", "A missing flag is shown as '-' in its position."
    assert describe(Permission.WRITE) == "-w-", "Always three characters, in the order r, w, x."
    assert describe(Permission(0)) == "---", "No permission: '---'."


def test_parse():
    assert parse("rwx") == Permission.READ | Permission.WRITE | Permission.EXECUTE, "'rwx' has all three flags."
    assert parse("r--") == Permission.READ, "'r--' is only READ."
    assert parse("-w-") == Permission.WRITE and parse("--x") == Permission.EXECUTE, "A letter in its own position sets its flag."
    assert parse("---") == Permission(0), "'---' is the empty permission."


def test_parse_errors():
    for bad in ("rw", "rwxx", "", "xwr", "rwz", "r-w"):
        with pytest.raises(ValueError):
            parse(bad)
    assert parse("rw-") == Permission.READ | Permission.WRITE, "Valid text still works after the errors."


def test_describe_and_parse_round_trip():
    for text in ("rwx", "r--", "-w-", "--x", "rw-", "r-x", "-wx", "---"):
        assert describe(parse(text)) == text, f"describe(parse({text!r})) should give {text!r} back."


def test_allows():
    granted = Permission.READ | Permission.WRITE
    assert allows(granted, Permission.READ) is True, "READ is granted."
    assert allows(granted, Permission.READ | Permission.WRITE) is True, "Needing two flags: both must be granted."
    assert allows(granted, Permission.EXECUTE) is False, "EXECUTE is not granted."
    assert allows(granted, Permission.READ | Permission.EXECUTE) is False, "Needing READ|EXECUTE when only READ is granted: all needed flags must be present."
    assert allows(Permission(0), Permission(0)) is True, "Needing nothing is always allowed."


def test_priority_is_an_intenum():
    assert Priority.HIGH == 3 and Priority.LOW < Priority.MEDIUM, "IntEnum members are ints: they compare with numbers and with each other."
    assert Priority.MEDIUM + 1 == Priority.HIGH, "IntEnum members support arithmetic as ints (the result is a plain int 3, equal to HIGH)."
    assert sorted([Priority.HIGH, Priority.LOW, Priority.MEDIUM]) == [Priority.LOW, Priority.MEDIUM, Priority.HIGH], "sorted() works on IntEnum members."
    assert isinstance(Priority.LOW, int), "IntEnum members are instances of int."
    assert Priority(2) is Priority.MEDIUM, "Lookup by value still works."


def test_highest():
    assert highest([Priority.LOW, Priority.HIGH, Priority.MEDIUM]) is Priority.HIGH, "highest() returns the member with the largest value."
    assert highest([]) is None, "An empty list gives None (max(..., default=None))."
    assert highest([Priority.LOW]) is Priority.LOW, "One element."
