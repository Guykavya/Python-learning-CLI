- Calling the parents by name (`TimestampMixin.__init__(self, ...)`). It works here by luck and
  runs a shared base twice in a diamond.
- A mixin that does not call `super().__init__(**kwargs)`. The chain stops there, and the classes
  after it in the MRO never set their attributes (`owner` is missing).
- A mixin that calls `super().__init__()` **without** `**kwargs`. The remaining keywords are lost:
  `owner` never reaches `OwnerMixin`, so Python says it is missing.
- Thinking `super()` means "my parent class". In `TimestampMixin`, `super()` is `OwnerMixin` for a
  `Document` and `object` for a `Note`.
- Swallowing leftovers (no `super()` call, or deleting unknown keys). A typo like `creatd=5` must
  reach `object.__init__` and raise `TypeError`.
- `self.readers = readers`. The object then shares the caller's list (or every object shares one).
