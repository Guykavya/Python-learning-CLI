from solution import build_profile


def test_example():
    assert build_profile("Asha", age=19, city="Pune") == {"name": "Asha", "age": 19, "city": "Pune"}


def test_name_only():
    assert build_profile("Ravi") == {"name": "Ravi"}, "With no extra keywords, details is {} and the profile has only the name."


def test_none_is_skipped():
    assert build_profile("Meena", email=None, phone="98111") == {"name": "Meena", "phone": "98111"}, (
        "Leave out details whose value is None.")


def test_falsy_values_kept():
    p = build_profile("Zoya", age=0, active=False, nickname="")
    assert p == {"name": "Zoya", "age": 0, "active": False, "nickname": ""}, (
        "0, False and '' are real values. Test `value is not None`, not just `if value:`.")


def test_key_order():
    p = build_profile("Kiran", city="Delhi", age=21)
    assert list(p) == ["name", "city", "age"], "'name' comes first, then the details in the order given."


def test_callers_dict_unchanged():
    extra = {"city": "Delhi", "age": 21, "email": None}
    build_profile("Kiran", **extra)
    assert extra == {"city": "Delhi", "age": 21, "email": None}, "Do not change the caller's dict."


def test_new_dict_each_time():
    a = build_profile("A", x=1)
    b = build_profile("B")
    assert b == {"name": "B"}, "Each call must build a new dict; nothing from an earlier call may leak in."
    assert a is not b
