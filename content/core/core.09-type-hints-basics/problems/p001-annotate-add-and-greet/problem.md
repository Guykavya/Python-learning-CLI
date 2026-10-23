# Annotate five small functions

`starter.py` has five working functions with **no** type hints. Copy it to `solution.py` and add
hints so that each header tells the truth about what goes in and what comes out.

| Function | Takes | Returns |
|---|---|---|
| `add(a, b)` | two whole numbers | their sum, a whole number |
| `greet(name)` | a name (text) | text such as `"Hello, Asha!"` |
| `is_adult(age)` | a whole number | `True` or `False` |
| `half(n)` | a whole number | a decimal number (`n / 2`) |
| `repeat(text, times)` | text and a whole number | text |

Do not change what the functions do. The tests read your hints with Python's
`typing.get_type_hints` and also run the functions, to prove that the hints did not break them.

**Example**

```python
def add(a: int, b: int) -> int:
    return a + b

add.__annotations__   # {'a': <class 'int'>, 'b': <class 'int'>, 'return': <class 'int'>}
```
