import pytest
from solution import power


def test_values():
    assert power(2, 10) == 1024
    assert power(5, 0) == 1
    assert power(-3, 3) == -27


def test_modulo_keyword():
    assert power(2, 10, modulo=1000) == 24, "(2 ** 10) % 1000 is 24."
    assert power(7, 2, modulo=7) == 0
    assert power(3, 10**6, modulo=13) == pow(3, 10**6, 13)


def test_base_exp_positional_only():
    with pytest.raises(TypeError):
        power(base=2, exp=3)
    with pytest.raises(TypeError):
        power(2, exp=3)


def test_modulo_keyword_only():
    with pytest.raises(TypeError):
        power(2, 3, 5)
