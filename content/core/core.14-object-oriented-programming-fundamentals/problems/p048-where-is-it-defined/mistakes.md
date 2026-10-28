- Using `hasattr(klass, name)`. It is `True` for inherited names too, so the first class in the MRO
  (the class itself) always "wins".
- Walking `__bases__` depth first. In a diamond that visits `Base` before `Right` and finds the
  overridden method. Python uses the C3 order in `__mro__`.
- Returning `klass.__name__` from `defined_in`. The task asks for the class object; only
  `all_definitions` returns names.
- Creating an instance to look for the name. Instance attributes from `__init__` are not class
  definitions, and creating objects can have side effects.
- Forgetting `object`. Names like `__init__` and `__repr__` are defined there when nobody else
  defines them.
