## Approach

Read each function from the inside: what does the body do to each parameter, and what does the `return` hand back? Then write the hint for **both** the container and its contents. The only subtle one is `by_length`: the keys are lengths (ints), and each value is a list of the words that have that length.

## Code

```python
def total(numbers: list[int]) -> int:
    result = 0
    for n in numbers:
        result += n
    return result


def longest(words: list[str]) -> str:
    return max(words, key=len)


def price_of(menu: dict[str, float], item: str) -> float:
    return menu[item]


def shout_all(words: list[str]) -> list[str]:
    return [w.upper() for w in words]


def centre(points: list[tuple[int, int]]) -> tuple[float, float]:
    xs = sum(x for x, y in points) / len(points)
    ys = sum(y for x, y in points) / len(points)
    return xs, ys


def by_length(words: list[str]) -> dict[int, list[str]]:
    groups: dict[int, list[str]] = {}
    for w in words:
        groups.setdefault(len(w), []).append(w)
    return groups
```

## Complexity

All O(n) in the number of items. The hints cost nothing at runtime.

## Another way

`centre` could return `tuple[float, ...]`, but that loses the information that there are exactly two numbers. A fixed tuple is the better description of "an x and a y".
