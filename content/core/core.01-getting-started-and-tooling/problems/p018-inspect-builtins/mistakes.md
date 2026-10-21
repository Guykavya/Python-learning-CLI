- `print("Type:", type(abs))` prints `Type: <class 'builtin_function_or_method'>`.
  You need the class's `__name__`.
- Calling the function by accident: `abs().__doc__` raises `TypeError` because
  `abs` needs an argument. You want the function object itself, without `()`.
- Writing `abs.__doc` or `abs._doc_`: dunder names have **two** underscores on
  each side. The `AttributeError` message shows the wrong name.
