- Forgetting the quotes: `print(Hello, World!)` is a `SyntaxError` because `!`
  cannot appear there, and `Hello` would be treated as a name.
- Small differences such as `Hello world` or a missing full stop. The checker
  compares text exactly, just like real automated tests do.
- Writing `Print(...)` with a capital P. Python names are case-sensitive, so this
  gives `NameError: name 'Print' is not defined`.
