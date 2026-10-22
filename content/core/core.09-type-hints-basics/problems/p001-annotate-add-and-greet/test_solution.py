from typing import get_type_hints

from solution import add, greet, half, is_adult, repeat


def test_add_hints():
    assert get_type_hints(add) == {"a": int, "b": int, "return": int}, (
        "add needs a: int, b: int and -> int. Every parameter has its own hint."
    )


def test_greet_hints():
    assert get_type_hints(greet) == {"name": str, "return": str}, (
        "greet takes a str and returns a str: def greet(name: str) -> str."
    )


def test_is_adult_hints():
    assert get_type_hints(is_adult) == {"age": int, "return": bool}, (
        "is_adult returns the result of a comparison, which is a bool: -> bool."
    )


def test_half_hints():
    assert get_type_hints(half) == {"n": int, "return": float}, (
        "half takes an int, but n / 2 is always a float, so the return hint is -> float."
    )


def test_repeat_hints():
    assert get_type_hints(repeat) == {"text": str, "times": int, "return": str}, (
        "repeat(text: str, times: int) -> str. Check that both parameters are annotated."
    )


def test_behaviour_unchanged():
    assert add(2, 3) == 5, "Adding hints must not change what add does."
    assert greet("Asha") == "Hello, Asha!", "greet must still build 'Hello, Asha!'."
    assert is_adult(18) is True and is_adult(17) is False, "is_adult: 18 and over is an adult."
    assert half(7) == 3.5, "half(7) is 3.5."
    assert repeat("ab", 3) == "ababab", "repeat must still repeat the text."
