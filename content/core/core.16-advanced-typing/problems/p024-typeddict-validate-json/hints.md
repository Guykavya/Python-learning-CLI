## Hint 1

What does a `TypedDict` class know about itself at run time? Look at `User.__required_keys__` and `typing.get_type_hints(User)` in the REPL. Which one tells you what **must** be present, and which one tells you the type of each key?

## Hint 2

`check_value` is a small recursive function: look at `typing.get_origin(tp)` and `get_args(tp)`. A union has origin `typing.Union` or `types.UnionType`; `list[X]` has origin `list`; a TypedDict is detected with `is_typeddict(tp)`. Check `bool` before (or instead of) `int`, because `isinstance(True, int)` is true.

## Hint 3

```
check_value(value, tp):
    if tp is None or NoneType: return value is None
    origin = get_origin(tp)
    union:   any(check_value(value, m) for m in get_args(tp))
    list:    isinstance(value, list) and all(check_value(v, X) for v in value)
    typeddict: try validate(value, tp) except (TypeError, ValueError): False
    bool:    isinstance(value, bool)
    int:     isinstance(value, int) and not isinstance(value, bool)
    float:   int or float, not bool
    else:    isinstance(value, tp)

validate(data, td):
    not dict -> TypeError
    missing = td.__required_keys__ - data.keys()  -> ValueError naming one
    for key in data: key not in hints -> ValueError; not check_value -> TypeError
```
