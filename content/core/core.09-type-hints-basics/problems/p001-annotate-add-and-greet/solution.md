## Approach

Write one hint per parameter (`name: type`) and one return hint (`-> type`). `half` returns a `float` even though it takes an `int`, because `/` always produces a float. `is_adult` returns the result of a comparison, which is a `bool`.

## Code

```python
def add(a: int, b: int) -> int:
    return a + b


def greet(name: str) -> str:
    return "Hello, " + name + "!"


def is_adult(age: int) -> bool:
    return age >= 18


def half(n: int) -> float:
    return n / 2


def repeat(text: str, times: int) -> str:
    return text * times
```

## Complexity

Annotations add no cost at runtime: Python stores them and never looks at them again. The functions are O(1) (except `repeat`, which is O(len(text) * times) for building the result).

## Another way

`float` would also be a fine hint for `a` and `b` in `add` if you wanted to allow decimals: an `int` is accepted wherever a `float` is expected. Here the table says whole numbers, so `int` is the precise choice.
