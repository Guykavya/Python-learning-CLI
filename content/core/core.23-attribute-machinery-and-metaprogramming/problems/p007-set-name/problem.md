# A field that knows its own name

A descriptor needs somewhere to keep **each instance's** value. The descriptor itself is shared
by every instance, so `self.value = ...` would give all objects the same value. The usual place
is the instance's own `__dict__`. But under which key? The descriptor does not know which
attribute name it was assigned to... unless it defines `__set_name__(self, owner, name)`. Python
calls that once, while the class is being created, for every class attribute that has it.

Copy `starter.py` to `solution.py` and fix the class `Field(default=None)`:

- `__set_name__` remembers the attribute name in `self.name`.
- Reading on an instance returns the value stored in `instance.__dict__[self.name]`, or
  `self.default` if nothing is stored.
- Assigning stores the value in `instance.__dict__[self.name]`, under the field's **own** name.
  (That is safe for a data descriptor: it is consulted before the instance dict, so the dict
  entry never hides it.)
- `del obj.field` removes the stored value, so the default shows again. If nothing was stored,
  raise `AttributeError` naming the field (not `KeyError`).
- Reading on the class returns the `Field` itself.

**Example**

```python
class Book:
    title = Field()
    pages = Field(default=0)

b = Book()
Book.title.name     # 'title'
b.title, b.pages    # (None, 0)
b.title = "Dune"
vars(b)             # {'title': 'Dune'}
Book().title        # None   (another book has its own value)
del b.title
b.title             # None
```
