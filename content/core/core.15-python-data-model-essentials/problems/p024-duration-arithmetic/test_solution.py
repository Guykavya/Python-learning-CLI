import pytest

from solution import Duration


def test_negative_rejected():
    with pytest.raises(ValueError):
        Duration(-1)


def test_of_and_str_repr():
    a = Duration.of(hours=1, minutes=2, seconds=3)
    assert a.seconds == 3723, "1h 2m 3s is 3600 + 120 + 3 = 3723 seconds."
    assert str(a) == "1:02:03", "str should be H:MM:SS with minutes and seconds padded to 2 digits."
    assert repr(a) == "Duration(3723)", "repr should be Duration(3723)."
    assert str(Duration(0)) == "0:00:00", "Zero is 0:00:00."
    assert str(Duration.of(hours=25)) == "25:00:00", "Hours may go past 24."
    assert Duration.of(minutes=90).seconds == 5400, "Parts are optional keywords."


def test_add_sub():
    assert (Duration(60) + Duration(30)).seconds == 90, "Add the seconds."
    assert isinstance(Duration(60) + Duration(30), Duration), "+ must return a Duration."
    assert (Duration(60) - Duration(30)).seconds == 30, "Subtract the seconds."
    assert (Duration(60) - Duration(60)).seconds == 0, "Subtracting an equal duration gives 0, which is allowed."


def test_sub_negative_raises():
    with pytest.raises(ValueError):
        Duration(10) - Duration(20)


def test_mul_both_sides():
    assert (Duration(30) * 3).seconds == 90 and (3 * Duration(30)).seconds == 90, "Duration * int and int * Duration (needs __rmul__)."
    assert isinstance(2 * Duration(5), Duration), "The result stays a Duration."
    with pytest.raises(ValueError):
        Duration(5) * -1
    with pytest.raises(TypeError):
        Duration(5) * 1.5
    with pytest.raises(TypeError):
        Duration(5) * Duration(5)


def test_floordiv():
    r = Duration(100) // 3
    assert isinstance(r, Duration) and r.seconds == 33, "Duration // int rounds down to whole seconds and stays a Duration."
    with pytest.raises(ZeroDivisionError):
        Duration(100) // 0
    with pytest.raises(TypeError):
        Duration(100) // 2.0


def test_truediv_is_a_float_ratio():
    r = Duration(90) / Duration(60)
    assert r == 1.5 and isinstance(r, float), "Duration / Duration is a plain float ratio: 90 / 60 = 1.5."
    with pytest.raises(ZeroDivisionError):
        Duration(1) / Duration(0)
    with pytest.raises(TypeError):
        Duration(10) / 2


def test_comparisons_and_hash():
    assert Duration(5) < Duration(6) and Duration(6) > Duration(5), "Ordering uses seconds."
    assert Duration(5) <= Duration(5) and Duration(5) >= Duration(5), "<= and >= hold when equal."
    assert Duration(5) == Duration(5) and Duration(5) != Duration(6), "Equality uses seconds."
    assert hash(Duration(5)) == hash(Duration(5)), "Equal durations need equal hashes."
    assert len({Duration(5), Duration(5), Duration(6)}) == 2, "A set should drop the duplicate."
    assert not (Duration(5) == 5), "A Duration is not equal to a plain int."


def test_other_types_typeerror():
    with pytest.raises(TypeError):
        Duration(5) + 5
    with pytest.raises(TypeError):
        Duration(5) < 5
    with pytest.raises(TypeError):
        Duration(5) - "a"
