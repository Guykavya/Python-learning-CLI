# Check installed versions and write lock lines

`requirements.txt` says which versions are **allowed** (`requests>=2.31,<3`). A **lock file** records the
exact version that was tested (`requests==2.32.3`), so every machine installs the same thing.
`pip freeze` shows what is installed right now. A small tool can compare the two: is every requirement
installed in an allowed version? If yes, pin it.

Write `make_lock(requirements, installed)` in `solution.py`.

- `requirements` is a list of `(name, specifier)` tuples, like the output of p012. Names are already
  normalised (lowercase, `-`). A name can appear **more than once**; then all its specifiers must hold.
- `installed` is a dict `name → version` as `pip freeze` prints it, for example `{"Flask": "3.0.2"}`.
  These names are **not** normalised: compare them after lowercasing and turning `_` and `.` into `-`.
- Versions are dotted numbers, and specifiers use only `==`, `!=`, `>=`, `<=`, `>`, `<` with commas, as
  in p013. You may copy your `satisfies` function from p013 into this file.

Return a tuple `(lock, problems)`:

- `problems`: a list of strings, one for each requirement that fails, in the order of `requirements`:
  - `"<name>: not installed"` when the package is missing, or
  - `"<name>: <version> does not satisfy <specifier>"` when the version is not allowed.
- `lock`: a list of `"<name>==<version>"` strings, sorted by name, one for each **distinct** required name
  whose requirements **all** passed. Installed packages that are not required are ignored.

**Example**

```python
requirements = [
    ("requests", ">=2.31,<3"),
    ("flask", ""),
    ("numpy", ">=1.26"),
    ("numpy", "<2"),
    ("rich", ""),
]
installed = {"Flask": "3.0.2", "requests": "2.32.3", "numpy": "2.1.0", "Typing_Extensions": "4.12.2"}

make_lock(requirements, installed)
# (['flask==3.0.2', 'requests==2.32.3'],
#  ['numpy: 2.1.0 does not satisfy <2', 'rich: not installed'])
```

`numpy` passes `>=1.26` but fails `<2`, so it is not locked. `typing-extensions` is installed but not
required, so it is ignored.
