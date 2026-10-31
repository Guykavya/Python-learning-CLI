import pytest

from solution import typechecked


def test_good_calls_pass():
    @typechecked
    def area(w: int, h: int = 1) -> int:
        return w * h

    assert area(2, 3) == 6, "Correct types: just call the function and return its result."
    assert area(4) == 4, "A default that was not passed is not checked."
    assert area(w=2, h=5) == 10, "Keyword arguments are checked by name too."


def test_bad_argument():
    called = []

    @typechecked
    def area(w: int, h: int = 1) -> int:
        called.append(1)
        return w * h

    with pytest.raises(TypeError) as info:
        area("2", 3)
    msg = str(info.value)
    assert "area" in msg and "'w'" in msg and "str" in msg, (
        f"The message must name the function, the parameter in quotes and the actual type. Got: {msg}"
    )
    with pytest.raises(TypeError) as info:
        area(2, h=1.5)
    assert "'h'" in str(info.value) and "float" in str(info.value), "Check keyword arguments too."
    assert called == [], "Check the arguments BEFORE calling the function."


def test_bad_return():
    @typechecked
    def half(n: int) -> int:
        return n / 2

    with pytest.raises(TypeError) as info:
        half(4)
    msg = str(info.value)
    assert "half" in msg and "return" in msg and "float" in msg, f"Check the result against the 'return' hint. Got: {msg}"


def test_unannotated_is_free():
    @typechecked
    def show(label, value: int):
        return f"{label}={value}"

    assert show(3.5, 2) == "3.5=2", "A parameter without a hint is not checked."
    assert show(label=[1], value=7) == "[1]=7"


def test_none_hint():
    @typechecked
    def log(msg: str) -> None:
        return None

    assert log("x") is None, "A None return hint becomes type(None); returning None passes."

    @typechecked
    def oops(msg: str) -> None:
        return msg

    with pytest.raises(TypeError):
        oops("x")


def test_generic_checks_outer_class():
    @typechecked
    def first(items: list[str], counts: dict[str, int] | None = None):
        return items[0] if items else None

    assert first(["a"]) == "a", "list[str]: only check that it is a list (use typing.get_origin)."
    assert first([1, 2]) == 1, "Only the outer class is checked, not the items."
    with pytest.raises(TypeError) as info:
        first(("a",))
    assert "'items'" in str(info.value) and "tuple" in str(info.value), "A tuple is not a list."
    assert first(["x"], {"a": 1}) == "x"
    assert first(["x"], None) == "x", "dict[str, int] | None: None matches the None member of the union."
    with pytest.raises(TypeError):
        first(["x"], [("a", 1)])


def test_union():
    @typechecked
    def label(x: int | str) -> str:
        return str(x)

    assert label(3) == "3" and label("a") == "a", "A union matches if ANY member matches (typing.get_args)."
    with pytest.raises(TypeError) as info:
        label(2.5)
    assert "float" in str(info.value)


def test_bad_call_shape_still_type_error():
    @typechecked
    def pair(a: int, b: int):
        return a + b

    with pytest.raises(TypeError):
        pair(1)


def test_metadata():
    @typechecked
    def f(x: int) -> int:
        """Doc."""
        return x

    assert f.__name__ == "f" and f.__doc__ == "Doc.", "Use functools.wraps."
