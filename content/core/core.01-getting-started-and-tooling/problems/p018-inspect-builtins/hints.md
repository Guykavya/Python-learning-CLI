## Hint 1

In the REPL, run `dir(abs)`. Can you find `__doc__`, `__name__` and
`__module__` in the list? What does each one show?

## Hint 2

`type(abs)` is a class object. Classes also have a `__name__`. So
`type(abs).__name__` is just the text `builtin_function_or_method`.

## Hint 3

```
print("Name:", abs.__name__)
print("Type:", type(abs).__name__)
print("Module:", abs.__module__)
print("Doc:", abs.__doc__)
... the same four lines for len ...
```
