from solution import mark_present, absent_students, sorted_register


def test_mark_present_new_register_each_call():
    a = mark_present("Asha")
    b = mark_present("Ravi")
    assert a == ["Asha"] and b == ["Ravi"], (
        f"Got {a} and {b}. Calls without a register share one list: the default [] is created once "
        "when def runs. Default to None and create the list inside the function.")


def test_mark_present_fills_callers_register():
    reg = []
    mark_present("Meena", reg)
    mark_present("Meena", reg)
    mark_present("Kiran", reg)
    assert reg == ["Meena", "Kiran"], (
        "The caller's register must be filled in place, without duplicates. "
        "If it stayed empty, you used `if not register` instead of `if register is None`.")


def test_absent_result():
    assert absent_students(["Asha", "Ravi", "Meena"], ["Ravi"]) == ["Asha", "Meena"]
    assert absent_students(["Asha"], []) == ["Asha"]
    assert absent_students([], ["Asha"]) == []


def test_absent_changes_nothing():
    everyone = ["Asha", "Ravi", "Meena"]
    reg = ["Ravi", "Zoya"]
    result = absent_students(everyone, reg)
    assert everyone == ["Asha", "Ravi", "Meena"], (
        "absent_students removed names from the caller's class list. Build a new list instead.")
    assert reg == ["Ravi", "Zoya"]
    assert result is not everyone, "Return a NEW list, not the caller's list."


def test_sorted_register_new_list():
    reg = ["ravi", "Asha", "meena", "Kiran"]
    result = sorted_register(reg)
    assert result == ["Asha", "Kiran", "meena", "ravi"], "Sort ignoring case: key=str.lower."
    assert reg == ["ravi", "Asha", "meena", "Kiran"], (
        "The register was reordered. list.sort() changes the caller's list; use sorted().")
