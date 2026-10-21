- Forgetting the brackets: `platform.python_version` (no `()`) prints
  `<function python_version at 0x...>` instead of calling the function.
- Typing `3.14` by hand. It is wrong on any other machine, which is exactly what
  the tests catch.
- Misspelling the attribute, for example `sys.version_info.minor_` or
  `sys.verison_info`: an `AttributeError` traceback tells you which name is wrong.
