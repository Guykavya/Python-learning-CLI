# Dataclass options: `default_factory`, `frozen`, `order`

`@dataclass` takes options, and `field(...)` takes options for single fields:

- `field(default_factory=list)`: call `list()` **for each new object** to get its default. A plain
  `= []` is refused (`ValueError: mutable default`), because all objects would share one list.
- `field(repr=False)`, `field(compare=False)`: leave a field out of `repr` or out of `==`.
- `@dataclass(frozen=True)`: assignment to fields raises `dataclasses.FrozenInstanceError`, and the
  class gets a `__hash__` (with `eq=True`), so objects work in sets and as dict keys.
- `@dataclass(order=True)`: generates `<`, `<=`, `>`, `>=` that compare the fields **as tuples, in
  the order they are written**.

Write two dataclasses in `solution.py`.

**`Playlist`**: `name: str`; `songs`: a list, default a **new empty list** for each playlist;
`plays: int = 0`, which is left out of `repr` **and** of `==`. The class stays mutable.

**`Version`**: `major: int`, `minor: int = 0`, `patch: int = 0`; frozen and ordered. Add a `__str__`
that returns `"major.minor.patch"` (for example `"1.2.0"`). `repr` stays the generated one.

**Example**

```python
a = Playlist("rock")
a.songs.append("x")
Playlist("jazz").songs                      # []
Playlist("p", ["a"], plays=5)               # Playlist(name='p', songs=['a'])
Version(1, 2, 3) < Version(1, 10, 0)        # True
sorted([Version(1, 5), Version(0, 9)])      # [Version(major=0, minor=9, patch=0), Version(major=1, minor=5, patch=0)]
Version(1).major = 2                        # FrozenInstanceError
```
