# Mangle a name like Python does

Inside a class body, Python renames ("mangles") names that start with two underscores:

```python
class Account:
    __pin = 1234          # stored as _Account__pin

print(vars(Account).keys())   # ... '_Account__pin' ...
```

The rule has a few corners that surprise people. Write `mangle(class_name, attr)` in `solution.py`. It
returns the name Python really stores when `attr` is written inside `class <class_name>:`.

The rules, in this order:

1. If `class_name` or `attr` is not a valid identifier (`str.isidentifier()` is `False`), raise
   `ValueError(f"not an identifier: {text!r}")` for the first bad one (check `class_name` first).
2. If `attr` does **not** start with `__` (two underscores), it is not mangled. Return it unchanged.
3. If `attr` **ends** with `__` (two underscores), it is a "dunder" name like `__init__`. Not mangled.
4. Remove all leading underscores from `class_name`. If nothing is left (the class name was only
   underscores), the name is not mangled.
5. Otherwise the result is `"_" + stripped_class_name + attr`.

## Example

```python
mangle("Account", "__pin")        # '_Account__pin'
mangle("Account", "_pin")         # '_pin'           one underscore: a convention only
mangle("Account", "__init__")     # '__init__'       dunder: never mangled
mangle("Account", "__pin_")       # '_Account__pin_' ends with ONE underscore: mangled
mangle("_Secret", "__key")        # '_Secret__key'   leading _ of the class removed
mangle("__Meta", "___x")          # '_Meta___x'      three underscores still start with two
mangle("___", "__x")              # '__x'            class name is only underscores
mangle("Account", "__")           # '__'             starts AND ends with __
mangle("my-class", "__x")         # ValueError: not an identifier: 'my-class'
```

The tests compare your function with real Python: they build a class with `exec` and look at the
keys of its `vars()`.
