## Approach

Filter first so you only square what you keep. `filter` and `map` are lazy: nothing is computed
until `list(...)` pulls the values through both stages. For the text, `map(int, ...)` converts
each piece; only then can the numbers be compared with 0.

## Code

```python
def squares_of_evens(numbers):
    """Return [n * n for each even n], using map and filter."""
    evens = filter(lambda n: n % 2 == 0, numbers)
    return list(map(lambda n: n * n, evens))


def parse_positive(text):
    """Return the positive integers in a whitespace-separated line, using map and filter."""
    return list(filter(lambda n: n > 0, map(int, text.split())))
```

## Complexity

O(n).

## Another way

Comprehensions say the same thing and many people find them clearer:
`[n * n for n in numbers if n % 2 == 0]` and `[n for n in map(int, text.split()) if n > 0]`.
