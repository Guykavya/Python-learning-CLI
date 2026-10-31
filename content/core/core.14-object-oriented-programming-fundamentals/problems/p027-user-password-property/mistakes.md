- `self.password = password` inside the setter. The setter calls itself again and again until
  `RecursionError`. Store into another name, `self._password_hash`.
- `self._password = password` in `__init__` (the plain text, bypassing the property). The checks do
  not run and the plain password sits in the object.
- Returning `None` from the getter instead of raising. Then `u.password` silently gives `None`.
- Raising `ValueError` from the getter. Reading a missing or forbidden attribute should raise
  `AttributeError`; tools like `hasattr` and `getattr(obj, name, default)` depend on that.
- Writing a setter for `is_locked`. A read-only property simply has no setter.
- Not resetting `_wrong` after a right attempt. Then 3 wrong attempts spread over months lock the user.
- Forgetting to reset `_wrong` in `unlock()`. The next single wrong attempt locks the user again.
