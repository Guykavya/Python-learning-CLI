## Hint 1

Everything you need is an attribute of `func.__code__`. Which attribute holds the local names,
and which holds the global and attribute names? Try `print(price_with_tax.__code__.co_names)`
in the REPL before writing any code.

## Hint 2

```
code = func.__code__
return {
    "name":      code.co_name,
    "argcount":  code.co_argcount,
    "locals":    sorted(code.co_varnames),
    "names":     sorted(code.co_names),
    "constants": [each c in code.co_consts if c is not None],
}
```

Use `is not None`, not `if c`: an empty string or `0.0` constant is falsy but must stay.
