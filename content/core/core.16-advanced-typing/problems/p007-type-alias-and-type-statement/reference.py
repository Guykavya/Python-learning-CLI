import math

type Point = tuple[float, float]
type Matrix = list[list[float]]
type Json = dict[str, Json] | list[Json] | str | int | float | bool | None


def distance(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def scale(m: Matrix, k: float) -> Matrix:
    return [[x * k for x in row] for row in m]


def count_leaves(value: Json) -> int:
    if isinstance(value, dict):
        return sum(count_leaves(v) for v in value.values())
    if isinstance(value, list):
        return sum(count_leaves(v) for v in value)
    return 1
