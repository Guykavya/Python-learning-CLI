## Approach

Cooperative `super()` (chapter section 12): every `__init__` takes only its own keywords and forwards
the rest with `super().__init__(**kwargs)`. `super()` follows the MRO of the **object** being built:

- `Document("Plan", owner="Kavya", created=3)` runs `Document` (takes `title`) -> `TimestampMixin`
  (takes `created`) -> `OwnerMixin` (takes `owner`) -> `object` (gets nothing).
- `Note("x", created=2)` runs `Note` -> `TimestampMixin` -> `object`. The same
  `TimestampMixin.__init__` now forwards to `object`, because `Note`'s MRO has no `OwnerMixin`.

The keyword-only `*` makes the mixin arguments safe: they cannot be filled by position by accident.
Anything left over when the chain reaches `object.__init__` is an unknown argument, and `object` raises
`TypeError`.

## Code

```python
class TimestampMixin:
    def __init__(self, *, created=0, **kwargs):
        self.created = created
        self.updated = created
        super().__init__(**kwargs)

    def touch(self, day):
        if day < self.created:
            raise ValueError("cannot update before creation")
        self.updated = day


class OwnerMixin:
    def __init__(self, *, owner, **kwargs):
        if not isinstance(owner, str) or owner == "":
            raise ValueError("owner must be a non-empty string")
        self.owner = owner
        super().__init__(**kwargs)

    def is_owned_by(self, name):
        return name == self.owner


class Document(TimestampMixin, OwnerMixin):
    def __init__(self, title, **kwargs):
        self.title = title
        super().__init__(**kwargs)

    def describe(self):
        return f"{self.title!r} by {self.owner}, created day {self.created}"


class SharedDocument(Document):
    def __init__(self, title, *, readers=(), **kwargs):
        self.readers = list(readers)
        super().__init__(title, **kwargs)


class Photo(OwnerMixin):
    def __init__(self, path, **kwargs):
        self.path = path
        super().__init__(**kwargs)


class Note(TimestampMixin):
    def __init__(self, text, **kwargs):
        self.text = text
        super().__init__(**kwargs)
```

## Complexity

O(k) per object for k classes in the MRO: each `__init__` runs once.

## Another way

The hard-coded version, `TimestampMixin.__init__(self, created=created)` followed by
`OwnerMixin.__init__(self, owner=owner)` inside `Document`, works for this one class. It breaks as
soon as two of those parents share a base with its own `__init__` (the diamond in p051), and every new
mixin means editing `Document`. Cooperative `super()` scales: you add a mixin to the bases list and
nothing else changes.
