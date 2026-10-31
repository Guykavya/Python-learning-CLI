- **Searching the source text with `in` or a regex.** `"os" in source` is true for `pos`,
  comments and strings. Work on the tree, where a name is a `Name` node.
- **Counting every `Name`, including stores.** `json = None` is not a use of the import.
- **Using `alias.name` for `import os.path`.** The bound name is `os`, and code uses `os.path...`.
- **Forgetting `kw_defaults`, or crashing on it.** Keyword-only parameters keep their defaults
  there, with `None` for parameters that have no default.
- **Treating `()` or `None` as mutable.** Tuples and `None` cannot be changed, so sharing them
  between calls is safe; that is why `def f(x=None): x = [] if x is None else x` is the fix.
- **Reporting each import line once.** `from os import sep, getcwd` with both unused is two
  problems.
- **Letting `SyntaxError` escape.** A linter must report broken files, not crash on them.
