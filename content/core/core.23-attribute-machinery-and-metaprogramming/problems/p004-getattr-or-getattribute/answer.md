**1. When.** `__getattribute__` is called for **every** attribute read on an instance, whether the
attribute exists or not. The default version, `object.__getattribute__`, is the normal lookup
(data descriptors, instance `__dict__`, class attributes, non-data descriptors). Only if that
raises `AttributeError` does Python call `__getattr__`. So `__getattr__` is a *fallback for
missing names*, and `__getattribute__` is the *front door for all names*.

**2. Choosing.**
- (a) Proxy: `__getattr__`. The proxy's own attributes (such as `self._target`) are found
  normally and fast; only unknown names are forwarded with `getattr(self._target, name)`.
- (b) Defaults: `__getattr__`. Stored names are found normally; missing ones fall back to the
  defaults.
- (c) Logging every read: `__getattribute__`, because `__getattr__` never sees names that exist.

**3. Risks of `__getattribute__`.**
- **Infinite recursion.** Any `self.anything` inside it calls it again. Even `self.__dict__`
  does. Get the normal value with `return super().__getattribute__(name)` (or
  `object.__getattribute__(self, name)`).
- **It is slow and global.** It runs on every read, including method lookups like
  `self.save`, so every access to the class pays for it, and a bug in it breaks the whole object.
- It also hides surprises: a property that raises `AttributeError` by mistake looks "missing"
  and silently falls through to `__getattr__`.

**4. Failing correctly.** Both must raise **`AttributeError`** (naming the attribute), never
`KeyError`, `None` or a made-up value. `getattr(obj, name, default)`, `hasattr`, `copy`, `pickle`
and many libraries probe objects for optional names like `__copy__` or `__setstate__` and rely
on `AttributeError` meaning "not there". A hook that returns something for every name makes
`hasattr` always `True`, and one that raises `KeyError` crashes `getattr` even with a default.
A hook that reads `self._data` before `__init__` has run (as `copy` does) must also be careful,
or it recurses.
