# Cooperative `__init__` with mixins and `**kwargs`

With multiple inheritance, every class in the MRO may need its own `__init__`. The rule that makes
this work is called **cooperative** `super()`:

- each `__init__` takes the keyword arguments **it** needs,
- passes all the other keyword arguments on with `super().__init__(**kwargs)`,
- and never calls a parent class by name.

Then every `__init__` in the MRO runs **exactly once**, and the last one, `object.__init__`, raises
`TypeError` if any unknown keyword is left over. That is a free typo check.

In `solution.py` write these classes:

### `TimestampMixin`

- `__init__(self, *, created=0, **kwargs)`: sets `self.created = created` and
  `self.updated = created`, and passes the rest on.
- `touch(self, day)`: sets `self.updated = day`. If `day < self.created`, raise
  `ValueError("cannot update before creation")` and change nothing.

### `OwnerMixin`

- `__init__(self, *, owner, **kwargs)`: `owner` is **required**. If it is not a non-empty `str`,
  raise `ValueError("owner must be a non-empty string")`. Sets `self.owner`, passes the rest on.
- `is_owned_by(self, name)`: `True` if `name == self.owner`.

### `Document(TimestampMixin, OwnerMixin)`

- `__init__(self, title, **kwargs)`: sets `self.title`, passes the rest on.
- `describe(self)`: returns `f"{self.title!r} by {self.owner}, created day {self.created}"`.

### `SharedDocument(Document)`

- `__init__(self, title, *, readers=(), **kwargs)`: sets `self.readers = list(readers)` (a new
  list for every object) and passes `title` and the rest on.

### `Photo(OwnerMixin)` and `Note(TimestampMixin)`

- `Photo.__init__(self, path, **kwargs)` sets `self.path`; `Note.__init__(self, text, **kwargs)`
  sets `self.text`. Both pass the rest on.

Every class above defines its own `__init__`, and every `__init__` calls `super().__init__(**kwargs)`
(not `TimestampMixin.__init__(self, ...)`). The tests count how often each `__init__` runs.

## Example

```python
d = Document("Plan", owner="Kavya", created=3)
d.describe()        # "'Plan' by Kavya, created day 3"
d.updated           # 3
d.touch(5); d.updated   # 5

Document.__mro__    # (Document, TimestampMixin, OwnerMixin, object)

s = SharedDocument("Notes", owner="Ravi", readers=["Asha"])
s.created, s.readers    # (0, ['Asha'])

Note("buy milk", created=2).created   # 2
Photo("cat.jpg", owner="Asha").path   # 'cat.jpg'

Document("Plan")                      # TypeError: missing keyword argument 'owner'
Document("Plan", owner="K", colour=1) # TypeError: object.__init__ gets the unknown 'colour'
```
