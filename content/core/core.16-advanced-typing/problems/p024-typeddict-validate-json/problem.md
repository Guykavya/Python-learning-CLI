# Validate JSON against a TypedDict

A `TypedDict` is only a hint: `json.loads` returns a plain `dict` that may have missing keys or
wrong types, and nothing checks it. To trust the data you must validate it at run time. Luckily
a `TypedDict` carries its own description, so one validator can handle **any** TypedDict.

In `solution.py` keep these definitions (they are in `starter.py`):

```python
class Address(TypedDict):
    city: str
    zip: str

class User(TypedDict):
    id: int
    name: str
    address: Address
    tags: NotRequired[list[str]]
    nickname: NotRequired[str | None]
```

and write:

1. `check_value(value, tp) -> bool`: is `value` acceptable for the type `tp`? Support:
   `int`, `float`, `str`, `bool`, `list[X]` (every item checked with `X`), unions such as
   `str | None` (any member fits), `None`, and a nested `TypedDict` (validated recursively).
   Two rules: `bool` is **not** accepted where `int` or `float` is wanted (`True` is not an id),
   but an `int` **is** accepted where `float` is wanted.
2. `validate(data, td)`: returns `data` itself when it fits the TypedDict `td`, otherwise raises:
   - `TypeError` if `data` is not a `dict`,
   - `ValueError` mentioning the key name if a **required** key is missing,
   - `ValueError` mentioning the key name if the data has a key that `td` does not declare,
   - `TypeError` mentioning the key name if a value has the wrong type.

   Use `td.__required_keys__` and `typing.get_type_hints(td)` (which hides `NotRequired[...]`
   and gives you plain types). `typing.is_typeddict(tp)` tells you whether `tp` is a TypedDict.
3. `load_user(text) -> User`: `json.loads(text)`, then `validate(..., User)`.
   Its return hint is `User`.

**Example**

```python
load_user('{"id": 1, "name": "Ada", "address": {"city": "Pune", "zip": "411001"}}')
# {'id': 1, 'name': 'Ada', 'address': {'city': 'Pune', 'zip': '411001'}}

load_user('{"id": "1", "name": "Ada", "address": {...}}')   # TypeError (id must be an int)
load_user('{"name": "Ada"}')                                 # ValueError (missing 'id')
```

**Remember**: at run time a `TypedDict` instance is a plain `dict`; the class itself exists only
so tools (and your validator) can read its annotations.
