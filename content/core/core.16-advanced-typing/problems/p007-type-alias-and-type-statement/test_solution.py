from typing import TypeAliasType, get_args, get_type_hints

import solution
from solution import count_leaves, distance, scale


def resolve(hint):
    """Follow `type X = ...` aliases so both alias styles compare equal."""
    while isinstance(hint, TypeAliasType):
        hint = hint.__value__
    return hint


def test_point_alias():
    assert hasattr(solution, "Point"), "Define the alias Point."
    assert resolve(solution.Point) == tuple[float, float], "Point is tuple[float, float]."


def test_matrix_alias():
    assert hasattr(solution, "Matrix"), "Define the alias Matrix."
    assert resolve(solution.Matrix) == list[list[float]], "Matrix is list[list[float]]."


def test_json_is_recursive_type_alias():
    assert hasattr(solution, "Json"), "Define the alias Json."
    j = solution.Json
    assert isinstance(j, TypeAliasType), "Json refers to itself, so write it with the type statement: type Json = ... (then it is a TypeAliasType)."
    assert j.__name__ == "Json", "The alias must be called Json."
    args = get_args(j.__value__)
    assert type(None) in args, "A Json value can be null: include None in the union."
    assert str in args and bool in args and int in args and float in args, "Json allows str, int, float and bool leaves."
    assert j in args or any(a is j for a in args) or any(j in get_args(a) for a in args), "The union must mention Json itself (a list of Json, a dict of Json)."


def test_function_hints_use_the_aliases():
    h = get_type_hints(distance)
    assert resolve(h["a"]) == tuple[float, float] and resolve(h["b"]) == tuple[float, float], "distance(a: Point, b: Point)."
    assert h["return"] is float, "distance -> float."
    h = get_type_hints(scale)
    assert resolve(h["m"]) == list[list[float]], "scale(m: Matrix, ...)."
    assert resolve(h["return"]) == list[list[float]], "scale returns a Matrix."
    assert h["k"] is float, "k: float."
    h = get_type_hints(count_leaves)
    assert h["value"] is solution.Json or resolve(h["value"]) is solution.Json.__value__ or resolve(h["value"]) == solution.Json.__value__, (
        "count_leaves(value: Json): use your Json alias for the parameter."
    )
    assert h["return"] is int, "count_leaves -> int."


def test_distance():
    assert distance((0.0, 0.0), (3.0, 4.0)) == 5.0, "3-4-5 triangle."
    assert distance((1.0, 1.0), (1.0, 1.0)) == 0.0, "Same point: distance 0."
    assert distance((-1.0, 0.0), (2.0, 4.0)) == 5.0, "Negative coordinates: subtract both coordinates."


def test_scale():
    assert scale([[1.0, 2.0], [3.0, 4.0]], 2.0) == [[2.0, 4.0], [6.0, 8.0]], "Multiply every number by k."
    assert scale([], 3.0) == [], "An empty matrix stays empty."


def test_scale_returns_new_matrix():
    m = [[1.0, 2.0]]
    out = scale(m, 10.0)
    assert m == [[1.0, 2.0]], "Do not change the input matrix: build a new one."
    assert out is not m and out[0] is not m[0], "Build new rows too, not only a new outer list."


def test_count_leaves():
    assert count_leaves({"a": [1, 2, {"b": None}], "c": "x"}) == 4, "Leaves: 1, 2, None, 'x'."
    assert count_leaves([]) == 0, "An empty list has no leaves."
    assert count_leaves({}) == 0, "An empty dict has no leaves."
    assert count_leaves(5) == 1, "A number alone is one leaf."
    assert count_leaves(None) == 1, "None is a leaf, not 'nothing'."
    assert count_leaves("hello") == 1, "A str is ONE leaf. Do not iterate over its characters."
    assert count_leaves([[], [[]], [[1]]]) == 1, "Only the 1 is a leaf."
    assert count_leaves({"k1": {"k2": {"k3": True}}}) == 1, "Keys are not leaves, only values are."
