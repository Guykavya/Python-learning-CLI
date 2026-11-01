# A family of validators

Writing `__get__`, `__set__` and `__set_name__` again for every kind of check is boring and
easy to get wrong. Better: write the descriptor machinery **once** in a base class and let each
subclass supply only the check. This is the template method pattern from core.22, applied to
descriptors.

Copy `starter.py` to `solution.py` and write:

**`Validator`**, an abstract base class (`abc.ABC`):

- `__set_name__` stores the field name in `self.name`.
- `__get__`: the descriptor itself on class access; otherwise the stored value, or
  `AttributeError` naming the field if it was never set.
- `__set__` calls `self.validate(value)` **first**, then stores the value per instance. If
  `validate` raises, nothing is stored.
- `validate(self, value)` is an `@abstractmethod`: it raises `TypeError` or `ValueError` for a
  bad value and returns nothing otherwise. So `Validator()` itself cannot be created, nor can a
  subclass that forgets `validate`.

**Three validators** (every message starts with the field name):

| Class | Accepts | Rejects with |
|---|---|---|
| `Range(min_value=None, max_value=None)` | an `int` or `float` (not `bool`) inside the limits, limits included; `None` means no limit | `TypeError("age must be a number, got str")`, `ValueError("age must be >= 0, got -1")`, `ValueError("age must be <= 150, got 200")` |
| `OneOf(*options)` | a value equal to one of the options | `ValueError("size must be one of 'S', 'M', 'L', got 'XL'")` (options and value shown with `repr`) |
| `NonEmptyStr(max_len=None)` | a `str` that is not empty or only spaces, and at most `max_len` characters | `TypeError("name must be a str, got int")`, `ValueError("name must not be empty")`, `ValueError("name must be at most 10 characters, got 12")` |

**Example**

```python
class Shirt:
    size = OneOf("S", "M", "L")
    price = Range(0, 500)
    label = NonEmptyStr(max_len=10)

s = Shirt()
s.size = "M"
s.price = 19.5
s.size = "XL"      # ValueError: size must be one of 'S', 'M', 'L', got 'XL'
s.size             # still 'M'
s.price = -1       # ValueError: price must be >= 0, got -1
s.label = "   "    # ValueError: label must not be empty
Shirt.price.name   # 'price'
```

Because the base class does all the work, a new rule is a few lines:

```python
class Even(Validator):
    def validate(self, value):
        if value % 2:
            raise ValueError(f"{self.name} must be even")
```
