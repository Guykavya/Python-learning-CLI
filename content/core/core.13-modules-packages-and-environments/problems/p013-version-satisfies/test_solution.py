import pytest

from solution import satisfies


def test_numeric_not_string_compare():
    assert satisfies("1.10", ">=1.9") is True, "Compare as tuples of ints: (1, 10) > (1, 9). As strings '1.10' < '1.9'."
    assert satisfies("1.9", ">=1.10") is False, "(1, 9) is older than (1, 10)."


def test_range():
    assert satisfies("1.5", ">=1.2,<2.0") is True, "1.5 is inside the range."
    assert satisfies("2.0", ">=1.2,<2.0") is False, "< is strict: 2.0 is not < 2.0. All clauses must hold."
    assert satisfies("1.1.9", ">=1.2,<2.0") is False, "1.1.9 is below 1.2."


def test_padding_with_zeros():
    assert satisfies("1.2", "==1.2.0") is True, "Pad the shorter tuple with zeros: (1, 2) becomes (1, 2, 0)."
    assert satisfies("1.2.0.0", "<=1.2") is True, "(1, 2, 0, 0) equals (1, 2, 0, 0) after padding."
    assert satisfies("1.2.1", "==1.2") is False, "(1, 2, 1) is not (1, 2, 0)."


def test_each_operator():
    cases = [
        ("3.0", "==3.0", True), ("3.0", "!=3.0", False), ("3.1", "!=3.0", True),
        ("3.0", ">=3.0", True), ("3.0", "<=3.0", True),
        ("3.0", ">3.0", False), ("3.0", "<3.0", False),
        ("3.0.1", ">3.0", True), ("2.9.9", "<3", True),
    ]
    for version, spec, want in cases:
        assert satisfies(version, spec) is want, (
            f"satisfies({version!r}, {spec!r}) should be {want}. Check two-char operators before '>' and '<'."
        )


def test_spaces_allowed():
    assert satisfies("3.0.1", " != 3.0.1 ") is False, "Strip spaces around the clause and after the operator."
    assert satisfies("1.5", ">= 1.2 , < 2.0") is True, "Spaces around commas and operators are allowed."


def test_empty_spec_allows_all():
    assert satisfies("0.1", "") is True, "An empty spec puts no limit on the version."
    assert satisfies("99.0", "   ") is True, "A spec of only spaces is empty too."


def test_returns_bool():
    assert isinstance(satisfies("1.0", ">=1"), bool), "Return True or False."


def test_unknown_operator_raises():
    for bad in ("~=1.0", "=1.0", "1.0", "=>1.0", "<>1.0"):
        with pytest.raises(ValueError):
            satisfies("1.0", bad)
