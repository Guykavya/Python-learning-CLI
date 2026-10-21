# Inspect built-ins like help() does

`help(abs)` shows documentation. Where does it come from? Every function object
carries information in special attributes:

- `__name__`: the function's name,
- `__module__`: the module it lives in,
- `__doc__`: its documentation string (docstring).

Write a script that prints, for `abs` and then for `len`:

```
Name: abs
Type: builtin_function_or_method
Module: builtins
Doc: Return the absolute value of the argument.
Name: len
Type: builtin_function_or_method
Module: builtins
Doc: Return the number of items in a container.
```

- `Type` is the **name** of the object's type: `type(abs).__name__`.
- Read everything from the objects. The tests check that you use `__name__`,
  `__module__`, `__doc__` and `type`, and that you did not paste the doc text.

(The doc text above is from Python 3.14. The tests compare with the Python you
actually run.)

**Example**

The first line of output is `Name: abs`.
