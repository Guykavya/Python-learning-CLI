- Copying every default in `__init__` (`self.port = Settings.port`, ...). Then `overrides()` returns
  everything, `reset` cannot restore the default, and later changes to the class default are ignored.
- Comparing with `Settings.port` instead of `getattr(type(self), name)`. A `ProductionSettings`
  then compares with the wrong default.
- Using `isinstance(value, type(default))`. `isinstance(True, int)` is `True`, so `port=True` would
  slip through. The problem asks for the exact type.
- Listing names with `vars(cls)` only. That misses inherited settings: `vars(ProductionSettings)` has
  no `debug`.
- Forgetting to skip callables: then `as_dict`, `names` and `reset` look like settings.
- `reset` written as `setattr(self, name, getattr(type(self), name))`. It looks right, but it stores
  a copy on the object, so the setting is still "overridden".
- `with_changes` returning `Settings(...)`. A production object would silently become a plain one.
