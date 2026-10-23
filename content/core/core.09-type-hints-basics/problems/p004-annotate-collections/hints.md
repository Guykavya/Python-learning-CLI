## Hint 1

Start with the easy ones: `total` and `longest` take a list. What goes in the brackets after `list`? Then do `price_of`: a dict needs two types, one for the keys and one for the values.

## Hint 2

`centre` takes a list of pairs, so you need a list *of tuples*: `list[tuple[int, int]]`. It returns one pair of decimals: a fixed tuple of two floats. For `by_length`, read the result from the outside in: a dict, from `int`, to a list of `str`.

## Hint 3

```
def total(numbers: list[int]) -> int:
def longest(words: list[str]) -> str:
def price_of(menu: dict[str, float], item: str) -> float:
def shout_all(words: list[str]) -> list[str]:
def centre(points: list[tuple[int, int]]) -> tuple[float, float]:
def by_length(words: list[str]) -> dict[int, list[str]]:
```
