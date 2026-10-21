## Approach

Functions are objects, and objects carry attributes. `help()` builds its page
from exactly these attributes (plus the parameter list).

## Code

```python
print("Name:", abs.__name__)
print("Type:", type(abs).__name__)
print("Module:", abs.__module__)
print("Doc:", abs.__doc__)
print("Name:", len.__name__)
print("Type:", type(len).__name__)
print("Module:", len.__module__)
print("Doc:", len.__doc__)
```

## What you learned

- `builtins` is the module that holds every name you can use without importing.
- `builtin_function_or_method` is the type of functions written in C inside
  CPython. Functions you write yourself later will have type `function`.
- Documentation is data stored on the object. When you write your own
  functions, a docstring you add becomes `__doc__` and appears in `help()`.

## Another way

`help(abs)` prints all of this in a pager; `python3 -m pydoc abs` does the same
from the terminal. The script approach shows that `help` is not magic.
