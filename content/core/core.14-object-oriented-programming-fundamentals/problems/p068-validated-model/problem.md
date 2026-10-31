# A tiny validated model with `Field` classes

Form libraries let you describe data by writing **fields as class attributes**:

```python
class User(Model):
    name = StrField(min_length=1, max_length=20)
    age = IntField(min_value=0, max_value=150)
    role = StrField(choices=["admin", "user"], required=False, default="user")
```

and then check a whole object at once, reporting **every** problem, not just the first. You build a
small version of this.

In `solution.py` write:

### `FieldError(Exception)`

`FieldError(field, message)` stores both; `str(e)` is `f"{field}: {message}"`.

### `Field`

- `Field(*, required=True, default=None)` stores both.
- `check(self, name, value)` handles the "missing" case and returns the cleaned value:
  - if `value is None`: return `self.default` if it is not `None`; else raise
    `FieldError(name, "is required")` if `required`; else return `None`;
  - otherwise return `value` unchanged.

### `IntField(Field)`

`IntField(*, min_value=None, max_value=None, **kwargs)` (the rest goes to `Field.__init__`).
`check(name, value)`: if `value is None`, return what `super().check(name, value)` returns. Otherwise:
not an `int` (or a `bool`) -> `FieldError(name, "must be an int")`; below `min_value` ->
`FieldError(name, f"must be >= {min_value}")`; above `max_value` -> `f"must be <= {max_value}"`.
Return the value.

### `StrField(Field)`

`StrField(*, min_length=0, max_length=None, choices=None, **kwargs)`. `check(name, value)`: `None` as
above. Otherwise, in this order: not a `str` -> `"must be a str"`; `len(value) < min_length` ->
`f"length must be >= {min_length}"`; `len(value) > max_length` -> `f"length must be <= {max_length}"`;
`choices` given and value not in it -> `"must be one of: " + ", ".join(choices)`. Return the value.

Each field reports only its **first** problem.

### `Model`

- Classmethod `fields(cls)`: a dict `name -> Field` with every `Field` defined as a class attribute in
  `cls` **or any base class**. Base-class fields come first, in the order they were written. If a
  subclass defines a field with the same name again, the subclass's `Field` wins but the name keeps its
  original position. (Hint: walk `reversed(cls.__mro__)` and look at `vars(klass)`.)
- `__init__(self, **values)`: for every name in `fields()`, sets the instance attribute to the given
  value, or `None` if not given. A keyword that is not a field raises
  `TypeError(f"unknown field {name!r}")` right away.
- `validate(self)`: checks every field in `fields()` order with `field.check(name, value)` and collects
  all `FieldError`s. If there are any, raise
  `ExceptionGroup(f"{ClassName} has {n} invalid field(s)", errors)` and change nothing. Otherwise store
  every cleaned value back on the instance (so defaults fill in) and return `self`.
- `to_dict(self)`: `{name: value}` for every field, in `fields()` order.

Instance attributes and class attributes can have the same name: `self.age = 30` lives in the
instance, while `type(self).age` is still the `IntField`. That is why `fields()` reads the classes.

## Example

```python
u = User(name="Kavya", age=21)
u.validate().to_dict()     # {'name': 'Kavya', 'age': 21, 'role': 'user'}

bad = User(name="", age=200, role="boss")
bad.validate()
# ExceptionGroup: User has 3 invalid field(s)
#   FieldError: name: length must be >= 1
#   FieldError: age: must be <= 150
#   FieldError: role: must be one of: admin, user

User(nmae="x")             # TypeError: unknown field 'nmae'

class Admin(User):
    role = StrField(choices=["admin"], required=False, default="admin")
    level = IntField(min_value=1)

list(Admin.fields())       # ['name', 'age', 'role', 'level']
```
