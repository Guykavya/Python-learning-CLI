## Hint 1

Write down the MRO of `SharedDocument`: `SharedDocument, Document, TimestampMixin, OwnerMixin,
object`. When `TimestampMixin.__init__` calls `super().__init__(**kwargs)`, which class is next for
a `Document` object? And for a `Note` object? `super()` means "the next class in the MRO of the
object being built", not "my parent".

## Hint 2

Each `__init__` picks out its own keyword (it appears in the signature, so it is **not** inside
`kwargs` any more) and forwards the rest. What is left in `kwargs` when the chain reaches
`object.__init__`? If the user made a typo, that typo is still there, and `object` raises.

## Hint 3

```text
TimestampMixin.__init__(self, *, created=0, **kwargs):
    self.created = created; self.updated = created
    super().__init__(**kwargs)

OwnerMixin.__init__(self, *, owner, **kwargs):
    check owner is a non-empty str, else ValueError
    self.owner = owner
    super().__init__(**kwargs)

Document.__init__(self, title, **kwargs):
    self.title = title
    super().__init__(**kwargs)

SharedDocument.__init__(self, title, *, readers=(), **kwargs):
    self.readers = list(readers)
    super().__init__(title, **kwargs)
```
