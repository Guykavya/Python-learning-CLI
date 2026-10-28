import ast
import inspect
from typing import Final, get_args, get_origin, get_type_hints

import pytest

import solution
from solution import Config, retry_delay


def is_final(annotation, *inner):
    """True for bare Final (when bare is accepted) or Final[T] with T in `inner`."""
    if annotation is Final:
        return None in inner
    return get_origin(annotation) is Final and get_args(annotation)[0] in inner


def module_hints():
    return get_type_hints(solution)


def test_max_retries_is_final():
    ann = module_hints().get("MAX_RETRIES")
    assert ann is not None, "MAX_RETRIES has no annotation. Write MAX_RETRIES: Final = 3."
    assert is_final(ann, None, int), "MAX_RETRIES must be annotated with Final (or Final[int])."


def test_str_and_float_constants_are_final_with_a_type():
    hints = module_hints()
    assert is_final(hints.get("API_URL"), str), "API_URL: Final[str] - give the type inside the brackets."
    assert is_final(hints.get("BASE_DELAY"), float), "BASE_DELAY: Final[float] - the value 0.5 is a float."
    assert is_final(hints.get("MAX_DELAY"), float), "MAX_DELAY: Final[float] - the value 8.0 is a float."


def test_tuple_constant_is_final():
    ann = module_hints().get("ALLOWED_METHODS")
    assert is_final(ann, None, tuple[str, ...]), (
        "ALLOWED_METHODS: Final = (...) or Final[tuple[str, ...]]. A tuple of any length needs the '...'."
    )


def test_class_attribute_is_final():
    hints = get_type_hints(Config)
    assert is_final(hints.get("DEFAULT_PORT"), int), "Config.DEFAULT_PORT: Final[int] = 8080 inside the class body."
    assert Config.DEFAULT_PORT == 8080, "Keep the value 8080."


def test_values_unchanged():
    assert solution.MAX_RETRIES == 3, "Do not change the constant values, only add the annotations."
    assert solution.API_URL == "https://api.example.com", "Do not change API_URL."
    assert solution.BASE_DELAY == 0.5 and solution.MAX_DELAY == 8.0, "Do not change the delays."
    assert solution.ALLOWED_METHODS == ("GET", "POST"), "Do not change ALLOWED_METHODS."


def test_function_hints():
    assert get_type_hints(retry_delay) == {"attempt": int, "return": float}, (
        "retry_delay(attempt: int) -> float."
    )


def test_retry_delay_values():
    assert retry_delay(0) == 0.5, "attempt 0 waits BASE_DELAY (0.5 * 2**0)."
    assert retry_delay(3) == 4.0, "attempt 3 waits 0.5 * 8 = 4.0."
    assert retry_delay(10) == 8.0, "The delay is capped by MAX_DELAY (8.0): use min(...)."


def test_negative_attempt_rejected():
    with pytest.raises(ValueError):
        retry_delay(-1)


def test_final_names_assigned_exactly_once():
    tree = ast.parse(inspect.getsource(solution))
    names = {"MAX_RETRIES", "API_URL", "BASE_DELAY", "MAX_DELAY", "ALLOWED_METHODS", "DEFAULT_PORT"}
    counts = dict.fromkeys(names, 0)
    for node in ast.walk(tree):
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
            targets = [node.target]
        for t in targets:
            if isinstance(t, ast.Name) and t.id in counts:
                counts[t.id] += 1
    for name, n in counts.items():
        assert n == 1, (
            f"{name} is assigned {n} times. A Final name is assigned exactly once, "
            "with the annotation: NAME: Final[...] = value."
        )
