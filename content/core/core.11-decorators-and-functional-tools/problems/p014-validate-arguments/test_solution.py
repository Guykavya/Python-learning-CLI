import pytest

from solution import in_range, typed


def make_add_marks():
    @typed(int, int)
    @in_range(0, 100)
    def add_marks(a, b):
        """Add two marks."""
        return a + b

    return add_marks


def test_good_call():
    add_marks = make_add_marks()
    assert add_marks(40, 35) == 75, "When all checks pass, call the function and return its result."
    assert add_marks(0, 100) == 100, "The range includes both ends: low <= x <= high."


def test_wrong_type():
    add_marks = make_add_marks()
    with pytest.raises(TypeError) as info:
        add_marks("40", 35)
    assert str(info.value) == "add_marks() argument 1 must be int, got str", (
        "Check isinstance(arg, wanted) for each argument; count from 1; use the type's __name__. "
        "If the name is 'wrapper', add @wraps(func) to BOTH decorators."
    )


def test_wrong_type_second_argument():
    add_marks = make_add_marks()
    with pytest.raises(TypeError) as info:
        add_marks(40, 3.5)
    assert str(info.value) == "add_marks() argument 2 must be int, got float", "The second argument is number 2. Use enumerate(..., start=1)."


def test_wrong_count():
    add_marks = make_add_marks()
    with pytest.raises(TypeError) as info:
        add_marks(40)
    assert str(info.value) == "add_marks() expects 2 positional arguments, got 1", "Compare len(args) with len(types) before checking each type."
    with pytest.raises(TypeError):
        add_marks(1, 2, 3)


def test_out_of_range():
    add_marks = make_add_marks()
    with pytest.raises(ValueError) as info:
        add_marks(40, 150)
    assert str(info.value) == "add_marks() argument 2 = 150 is outside 0..100", "Raise ValueError naming the argument number, its value and the range."
    with pytest.raises(ValueError):
        add_marks(-1, 5)


def test_metadata_kept():
    add_marks = make_add_marks()
    assert add_marks.__name__ == "add_marks", "Stacked decorators need @wraps(func) on every wrapper, or the name becomes 'wrapper'."
    assert add_marks.__doc__ == "Add two marks.", "wraps keeps the docstring."


def test_in_range_ignores_non_numbers():
    @in_range(1, 5)
    def label(n, text):
        return f"{text}{n}"

    assert label(3, "room ") == "room 3", "in_range checks only int and float arguments. Leave strings alone."


def test_keywords_not_checked():
    @typed(str)
    def greet(name, punct="!"):
        return name + punct

    assert greet("Ann", punct="?") == "Ann?", "Keyword arguments are passed on without a check and are not counted."


def test_no_call_on_failure():
    calls = []

    @typed(int)
    def f(x):
        calls.append(x)
        return x

    with pytest.raises(TypeError):
        f("no")
    assert calls == [], "Check the arguments BEFORE calling the function. A bad call must not run the body."
