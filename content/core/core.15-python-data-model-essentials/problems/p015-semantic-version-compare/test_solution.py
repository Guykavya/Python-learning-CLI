import pytest

from solution import Version


def test_parse():
    v = Version("1.10.2")
    assert (v.major, v.minor, v.patch) == (1, 10, 2), "Version('1.10.2') should have major 1, minor 10, patch 2 as ints."


@pytest.mark.parametrize("bad", ["1.2", "1.2.3.4", "a.b.c", "1..3", "", "1.2.x", "-1.2.3"])
def test_invalid_raises_valueerror(bad):
    with pytest.raises(ValueError):
        Version(bad)


def test_numeric_not_text_comparison():
    assert Version("1.10.0") > Version("1.2.0"), "Compare numbers, not text: 10 > 2, even though '10' < '2' as text."
    assert Version("0.10.0") > Version("0.9.9"), "minor 10 beats minor 9."


def test_order_levels():
    assert Version("2.0.0") > Version("1.99.99"), "major beats minor and patch."
    assert Version("1.2.3") < Version("1.2.4"), "patch decides when major and minor are equal."


def test_all_operators():
    a, b = Version("1.2.3"), Version("1.2.4")
    assert a < b and a <= b and b > a and b >= a, "All four ordering operators must work."
    assert a <= Version("1.2.3") and a >= Version("1.2.3"), "<= and >= hold for equal versions."


def test_equality_and_leading_zeros():
    assert Version("1.02.0") == Version("1.2.0"), "Leading zeros do not matter: compare ints."
    assert Version("1.2.0") != Version("1.2.1"), "Different patch means not equal."
    assert not (Version("1.2.0") == "1.2.0"), "A Version is not equal to a plain string."


def test_hash_matches_eq():
    assert hash(Version("1.02.0")) == hash(Version("1.2.0")), "Equal versions need equal hashes: hash the int tuple, not the text."
    assert len({Version("1.2.0"), Version("1.02.0"), Version("1.3.0")}) == 2, "A set must treat 1.02.0 and 1.2.0 as one."


def test_sorted():
    vs = [Version("2.0.0"), Version("1.10.0"), Version("1.9.3")]
    assert [str(v) for v in sorted(vs)] == ["1.9.3", "1.10.0", "2.0.0"], "sorted() should use the numeric order."


def test_str_repr_and_foreign():
    assert str(Version("1.02.0")) == "1.2.0", "str() shows the normalised text: leading zeros removed."
    assert repr(Version("1.2.0")) == "Version('1.2.0')", "repr should be Version('1.2.0')."
    with pytest.raises(TypeError):
        Version("1.0.0") < "2.0.0"
