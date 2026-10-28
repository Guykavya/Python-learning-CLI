import pytest

from solution import Frac


def test_reduces_and_fixes_sign():
    f = Frac(2, 4)
    assert (f.num, f.den) == (1, 2), "Frac(2, 4) should reduce to 1/2. Divide by math.gcd(num, den)."
    g = Frac(1, -2)
    assert (g.num, g.den) == (-1, 2), "Keep the denominator positive: Frac(1, -2) is -1/2."
    assert (Frac(0, 5).num, Frac(0, 5).den) == (0, 1), "Zero is 0/1."


def test_zero_denominator():
    with pytest.raises(ZeroDivisionError):
        Frac(1, 0)


def test_add_sub_mul_div():
    a, b = Frac(1, 2), Frac(1, 3)
    assert a + b == Frac(5, 6), "1/2 + 1/3 = 5/6."
    assert a - b == Frac(1, 6), "1/2 - 1/3 = 1/6."
    assert a * b == Frac(1, 6), "1/2 * 1/3 = 1/6."
    assert a / b == Frac(3, 2), "(1/2) / (1/3) = 3/2: multiply by the inverse."


def test_with_ints_both_sides():
    a = Frac(1, 2)
    assert a + 1 == Frac(3, 2) and 1 + a == Frac(3, 2), "Frac + int and int + Frac (needs __radd__)."
    assert a * 4 == 2 and 4 * a == 2, "Frac * int and int * Frac (needs __rmul__)."
    assert a - 1 == Frac(-1, 2), "Frac - int."
    assert 1 - Frac(1, 4) == Frac(3, 4), "1 - 1/4 is 3/4: __rsub__ must compute other - self, not self - other."
    assert 1 / Frac(2, 3) == Frac(3, 2), "1 / (2/3) is 3/2: __rtruediv__ must compute other / self."
    assert Frac(2, 3) / 2 == Frac(1, 3), "Frac / int."


def test_division_by_zero_fraction():
    with pytest.raises(ZeroDivisionError):
        Frac(1, 2) / Frac(0, 1)
    with pytest.raises(ZeroDivisionError):
        1 / Frac(0, 3)


def test_equality_and_hash():
    assert Frac(2, 4) == Frac(1, 2), "Equal after reduction."
    assert Frac(4, 2) == 2 and 2 == Frac(4, 2), "A Frac with den 1 equals the int."
    assert Frac(1, 2) != Frac(1, 3), "Different values are not equal."
    assert hash(Frac(2, 4)) == hash(Frac(1, 2)), "Equal fractions need equal hashes."
    assert hash(Frac(4, 2)) == hash(2), "Frac(4, 2) == 2, so their hashes must be equal."
    assert len({Frac(1, 2), Frac(2, 4), Frac(1, 3)}) == 2, "A set should hold 1/2 once."


def test_ordering():
    assert Frac(1, 3) < Frac(1, 2) and Frac(1, 2) > Frac(1, 3), "1/3 < 1/2."
    assert Frac(-1, 2) < Frac(1, 3), "Negative fractions are smaller."
    assert Frac(1, 2) <= Frac(2, 4) and Frac(1, 2) >= Frac(2, 4), "<= and >= hold for equal fractions."
    assert Frac(1, 2) < 1 and 1 > Frac(1, 2) and Frac(3, 2) > 1, "Compare with ints too."
    assert [repr(f) for f in sorted([Frac(1, 2), Frac(1, 3), Frac(1, 4)])] == ["Frac(1, 4)", "Frac(1, 3)", "Frac(1, 2)"], "sorted() should work."


def test_text_and_float():
    assert repr(Frac(1, 2)) == "Frac(1, 2)", "repr should be Frac(1, 2)."
    assert str(Frac(1, 2)) == "1/2", "str should be 1/2."
    assert str(Frac(6, 2)) == "3", "A whole number prints without /1."
    assert str(Frac(-1, 2)) == "-1/2", "The sign goes on the numerator."
    assert float(Frac(1, 4)) == 0.25, "float(Frac(1, 4)) should be 0.25. Define __float__."


def test_other_types_raise_typeerror():
    with pytest.raises(TypeError):
        Frac(1, 2) + "a"
    with pytest.raises(TypeError):
        Frac(1, 2) + 0.5
    with pytest.raises(TypeError):
        Frac(1, 2) < "a"
    assert not (Frac(1, 2) == "1/2"), "A Frac is not equal to a string."
