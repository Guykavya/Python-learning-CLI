- Mangling dunders. `__init__` must stay `__init__`, or no class could have a constructor.
- Treating one trailing underscore like two. `__pin_` is mangled; only `__` at the end stops it.
- Using `strip("_")` on the class name. Only **leading** underscores are removed: `My_Class_` keeps
  its trailing underscore.
- Forgetting the all-underscore class name. `"___".lstrip("_")` is `""`, and Python then leaves the
  name alone instead of producing `_` + `""` + `__x`.
- Adding two underscores in front (`__Account__pin`). The prefix is a single `_`.
- Thinking mangling makes the attribute private. Anyone can still read `obj._Account__pin`.
