import random

import pytest

from solution import mro


def python_error(cls_name, bases_map):
    try:
        python_mro(cls_name, bases_map)
    except TypeError as e:
        return str(e)
    return None


def python_mro(cls_name, bases_map):
    """Build the classes in real Python and return the MRO names (or the TypeError message)."""
    built = {"object": object}

    def build(name):
        if name not in built:
            bases = tuple(build(b) for b in bases_map[name])
            built[name] = type(name, bases, {})
        return built[name]

    return [c.__name__ for c in build(cls_name).__mro__]


def check(cls_name, bases_map, why=""):
    want = python_mro(cls_name, bases_map)
    got = mro(cls_name, bases_map)
    assert got == want, f"mro({cls_name!r}, {bases_map}) should be {want}, got {got}. {why}"


def test_single_class():
    check("A", {"A": []}, "A class with no bases: [name, 'object'].")


def test_object():
    assert mro("object", {}) == ["object"], "mro('object', ...) is just ['object']."


def test_explicit_object_base():
    check("A", {"A": ["object"]}, "Writing 'object' as a base explicitly gives the same MRO as no bases.")


def test_chain():
    check("C", {"A": [], "B": ["A"], "C": ["B"]}, "Single inheritance: walk up the chain.")


def test_diamond():
    m = {"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"]}
    check("D", m, "In a diamond, A comes after BOTH B and C. Depth-first (D, B, A, C) is wrong.")
    assert mro("D", m) == ["D", "B", "C", "A", "object"], "The classic diamond: D, B, C, A, object."


def test_order_of_bases_matters():
    check("E", {"A": [], "B": ["A"], "C": ["A"], "E": ["C", "B"]}, "E(C, B) puts C before B.")


def test_mixin_and_diamond():
    m = {"Base": [], "LogMixin": [], "Left": ["Base"], "Right": ["Base"], "Bottom": ["LogMixin", "Left", "Right"]}
    check("Bottom", m, "Same hierarchy as p061: Bottom, LogMixin, Left, Right, Base, object.")


def test_wikipedia_example():
    m = {"O": [], "A": ["O"], "B": ["O"], "C": ["O"], "D": ["O"], "E": ["O"],
         "K1": ["A", "B", "C"], "K2": ["D", "B", "E"], "K3": ["D", "A"], "Z": ["K1", "K2", "K3"]}
    check("Z", m, "This is the standard C3 example. Check that you remove a chosen head from EVERY list.")
    assert mro("Z", m) == ["Z", "K1", "K2", "K3", "D", "A", "B", "C", "E", "O", "object"]


def test_tuples_allowed():
    check("D", {"A": (), "B": ("A",), "C": ("A",), "D": ("B", "C")}, "Bases may be given as tuples.")


def test_does_not_change_input():
    m = {"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"]}
    copy = {k: list(v) for k, v in m.items()}
    mro("D", m)
    mro("D", m)
    assert m == copy, "Do not change the lists in bases_map. merge must work on copies."


def inconsistent(cls_name, bases_map, bases_text):
    with pytest.raises(TypeError) as py:
        python_mro(cls_name, bases_map)
    try:
        got = mro(cls_name, bases_map)
    except TypeError as e:
        error = e
    else:
        pytest.fail(
            f"mro({cls_name!r}, ...) returned {got}, but Python refuses this hierarchy. When no head of the "
            "merge is free (each one is in the tail of some list), raise TypeError."
        )
    msg = f"Cannot create a consistent method resolution order (MRO) for bases {bases_text}"
    assert str(error) == msg, (
        f"Use the message {msg!r}. Got {str(error)!r}. The names are the distinct heads of the lists "
        "that are still not empty when the merge gets stuck."
    )
    assert str(py.value) == msg, "test data error"


def test_class_before_its_subclass():
    inconsistent("Z", {"X": [], "Y": ["X"], "Z": ["X", "Y"]}, "X, Y")


def test_conflicting_orders():
    m = {"A": [], "B": [], "AB": ["A", "B"], "BA": ["B", "A"], "Bad": ["AB", "BA"]}
    inconsistent("Bad", m, "A, B")


def test_conflict_deep_down():
    m = {"Base": [], "LogMixin": [], "Left": ["Base"], "Right": ["Base"],
         "Bottom": ["LogMixin", "Left", "Right"], "Other": ["Right", "Left"], "Mixed": ["Bottom", "Other"]}
    inconsistent("Mixed", m, "Left, Right")


def test_duplicate_base():
    with pytest.raises(TypeError, match="duplicate base class A"):
        mro("X", {"A": [], "X": ["A", "A"]})


def test_unknown_base():
    with pytest.raises(KeyError):
        mro("X", {"X": ["Missing"]})


def random_hierarchy(rng, size):
    """Random classes; each picks up to 3 earlier classes as bases. Returns (bases_map, list of class names)."""
    bases_map = {}
    names = []
    for i in range(size):
        name = f"C{i}"
        k = rng.randint(0, min(3, len(names)))
        bases_map[name] = rng.sample(names, k)
        try:
            python_mro(name, bases_map)
        except TypeError:
            yield dict(bases_map), name, False  # inconsistent: test it, then forget the class
            del bases_map[name]
            continue
        names.append(name)
        yield dict(bases_map), name, True


def test_random_hierarchies_against_python():
    rng = random.Random(1414)
    good = bad = 0
    for _ in range(60):
        for bases_map, name, ok in random_hierarchy(rng, 12):
            if ok:
                check(name, bases_map, "Random hierarchy: your merge differs from Python's.")
                good += 1
            else:
                try:
                    got = mro(name, bases_map)
                except TypeError as e:
                    error = e
                else:
                    pytest.fail(f"mro({name!r}, {bases_map}) returned {got}, but Python raises TypeError for it.")
                want = python_error(name, bases_map)
                assert str(error) == want, (
                    f"mro({name!r}, {bases_map}): Python says {want!r}, you said {str(error)!r}. "
                    "List the distinct heads of the lists that are left when the merge is stuck."
                )
                bad += 1
    assert good > 100 and bad > 10, "test data error"
