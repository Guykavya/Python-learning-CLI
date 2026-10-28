- Leaving `print(report(sys.stdin.read(), n))` at the top level of a module. Every import then waits
  for keyboard input.
- Writing `from clean import words` (absolute, without the package). It only works by accident when
  `textkit/` itself is on `sys.path`, and fails from the project folder.
- Copying `words` into `stats.py` "to be safe". Two copies drift apart; a bug fixed in one stays in the other.
- Naming the module `report.py` and doing `from .report import report` in `__init__.py`. The function
  replaces the submodule on the package, so `textkit.report` is no longer the module.
- Making `clean` import from `stats` or `reporting`. Arrows going both ways create a circular import.
- Writing `"\n".join` inside the triple-quoted file text. The file then contains a real line break
  inside the string literal, which is a syntax error.
