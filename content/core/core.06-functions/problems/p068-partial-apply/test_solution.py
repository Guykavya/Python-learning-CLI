from solution import partial_apply


def describe(name, age, city="Pune", sep=", "):
    return f"{name}{sep}{age}{sep}{city}"


def test_positional_prefill():
    asha = partial_apply(describe, "Asha")
    assert asha(19) == "Asha, 19, Pune", "Stored positional arguments come FIRST, then the new ones."
    assert asha(20, city="Delhi") == "Asha, 20, Delhi"


def test_keyword_override_does_not_stick():
    dashed = partial_apply(describe, sep=" - ")
    assert dashed("Ravi", 21) == "Ravi - 21 - Pune"
    assert dashed("Ravi", 21, sep="/") == "Ravi/21/Pune", "A keyword given at call time overrides the stored one."
    assert dashed("Meena", 30) == "Meena - 30 - Pune", (
        "The override changed the stored keywords. Build a NEW merged dict each call; do not update the stored one.")


def test_builtin():
    assert partial_apply(int, base=2)("1011") == 11
    assert partial_apply(max, 10)(3, 7) == 10


def test_nothing_stored():
    g = partial_apply(describe)
    assert g("Kiran", 5, city="Goa") == "Kiran, 5, Goa"


def test_everything_stored():
    g = partial_apply(describe, "Zoya", 40, city="Agra")
    assert g() == "Zoya, 40, Agra"


def test_independent():
    a = partial_apply(describe, "A")
    b = partial_apply(describe, "B")
    assert a(1) == "A, 1, Pune" and b(2) == "B, 2, Pune"


def test_no_functools_partial():
    from pathlib import Path
    assert "partial(" not in Path(__file__).with_name("solution.py").read_text().replace("partial_apply(", ""), (
        "Write it yourself; do not use functools.partial.")
