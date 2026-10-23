# Annotate functions with collections

`starter.py` has six working functions that take or return collections, with no hints. Copy it to
`solution.py` and add hints. Read each body to see what really goes in and comes out.

| Function | Takes | Returns |
|---|---|---|
| `total(numbers)` | a list of whole numbers | their sum |
| `longest(words)` | a list of strings | the longest string (the first one if there is a tie) |
| `price_of(menu, item)` | a dict from item name to price (decimal), and an item name | the price |
| `shout_all(words)` | a list of strings | a new list of upper-case strings |
| `centre(points)` | a list of `(x, y)` pairs of whole numbers | the average x and the average y as a pair of decimals |
| `by_length(words)` | a list of strings | a dict from a length to the list of words of that length |

**Example**

```python
by_length(["a", "bb", "c"])   # {1: ["a", "c"], 2: ["bb"]}
```
(the hint for the result is `dict[int, list[str]]`)
