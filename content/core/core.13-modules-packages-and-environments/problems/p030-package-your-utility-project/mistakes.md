- Creating folders before checking the arguments. A failed call then leaves a half-made project, and
  the next call says "exists".
- Writing TOML strings with f-strings and plain quotes: `description = "Says "hi""` is invalid TOML.
  Escape with `json.dumps`.
- Writing `word-tools = "..."` as a bare key is fine, but a name with a dot (`word.tools = ...`) would
  become a nested table. Quote the key.
- Forgetting `[tool.setuptools.packages.find] where = ["src"]` (or relying on luck): the wheel then
  contains no code at all.
- Putting the package next to `pyproject.toml` instead of under `src/`. Tests then import the project
  folder, not what users install.
- `__main__.py` that calls `main()` without `sys.exit(...)`: the exit code from `main` is lost and an
  error still exits with 0.
- Calling `main()` at the top level of `cli.py` or `__main__.py` without the `__name__` guard: importing
  the module runs the program.
- Using f-strings for the code templates: every `{` in the generated code (like `f"%(prog)s {__version__}"`)
  must then be doubled. Placeholders with `replace` avoid that.
- Forgetting that `\n` inside a `'''` template becomes a real newline in the generated file.
