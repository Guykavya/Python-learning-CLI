import ast
import math
from pathlib import Path

import solution
from solution import area, register, shape_names

TREE = ast.parse(Path(solution.__file__).read_text())


def _func(name):
    for node in ast.walk(TREE):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"function {name} is missing")


def test_builtin_shapes():
    assert math.isclose(area({"type": "circle", "r": 2}), math.pi * 4), "circle: pi * r**2."
    assert area({"type": "rect", "w": 3, "h": 4}) == 12, "rect: w * h."
    assert area({"type": "square", "side": 5}) == 25, "square: side ** 2."
    assert area({"type": "rect", "w": 0, "h": 9}) == 0, "A zero side gives area 0."


def test_unknown_shape_raises_value_error():
    try:
        area({"type": "blob"})
    except ValueError as e:
        assert "blob" in str(e), "The error message must contain the unknown name ('blob')."
    except Exception as e:
        raise AssertionError(f"An unknown shape must raise ValueError, not {type(e).__name__}. Convert the KeyError.")
    else:
        raise AssertionError("An unknown shape must raise ValueError.")


def test_register_a_new_shape_without_editing_the_module():
    @register("triangle")
    def triangle(shape):
        return 0.5 * shape["b"] * shape["h"]

    assert area({"type": "triangle", "b": 4, "h": 3}) == 6.0, (
        "A shape registered from outside must work: area must look the shape up in the registry, not in an if/elif chain."
    )
    assert callable(triangle) and triangle({"b": 2, "h": 2}) == 2.0, "The decorator must return the function unchanged."


def test_register_as_a_plain_call():
    register("hexagon")(lambda s: 2.598 * s["side"] ** 2)
    assert math.isclose(area({"type": "hexagon", "side": 1}), 2.598), "register(name)(func) works like the decorator."


def test_shape_names_and_duplicates():
    names = shape_names()
    assert names == sorted(names), "shape_names() returns a sorted list."
    assert {"circle", "rect", "square"} <= set(names), "The three built-in shapes are registered."
    register("one-off")(lambda s: 1)
    assert "one-off" in shape_names(), "A newly registered name appears in shape_names()."
    try:
        register("circle")(lambda s: 0)
    except ValueError:
        pass
    else:
        raise AssertionError("Registering a name twice must raise ValueError (silent replacement hides mistakes).")
    assert math.isclose(area({"type": "circle", "r": 1}), math.pi), "A refused registration must not change the old function."


def _chain_length(node):
    n = 1
    while len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
        node = node.orelse[0]
        n += 1
    return n


def test_area_has_no_long_if_chain():
    for node in ast.walk(_func("area")):
        if isinstance(node, ast.If):
            assert _chain_length(node) <= 2, (
                "area still has an if/elif chain of 3 or more branches. Look the function up in a dict and call it; "
                "a new shape must not need an edit here."
            )


def test_area_does_not_name_the_shapes():
    for node in ast.walk(_func("area")):
        if isinstance(node, ast.Constant) and node.value in ("circle", "rect", "square"):
            raise AssertionError(f"area mentions the shape name {node.value!r}. Shape formulas belong in registered functions.")
