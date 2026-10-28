- Walking `cls.__mro__` from `cls` to `object` and letting base classes overwrite. Then `User.role`
  replaces `Admin.role`, the opposite of overriding.
- Using `dir(cls)` for the field names. It is sorted alphabetically, so the definition order is lost.
- Reading `self.age` to find the field. After `__init__`, `self.age` is the **value**; the `Field` is
  on the class.
- Stopping at the first bad field. The whole point is to report every problem in one go.
- Storing the cleaned values while still checking. A failure halfway leaves the object half-updated.
- Treating `True` as an int and `0` or `""` as missing. Only `None` means missing.
- Forgetting `**kwargs` in `IntField.__init__`. Then `IntField(required=False)` is a `TypeError`.
