## Hint 1

Do the rules in order and return as soon as one says "not mangled". Which two string methods tell
you whether a text starts or ends with something? What does `"__Meta".lstrip("_")` give, and how is it
different from `"_a_".strip("_")`?

## Hint 2

```text
mangle(class_name, attr):
    for text in (class_name, attr):
        if not text.isidentifier(): raise ValueError(f"not an identifier: {text!r}")
    if attr does not start with "__": return attr
    if attr ends with "__": return attr
    stripped = class_name without leading "_"
    if stripped == "": return attr
    return "_" + stripped + attr
```

Check `"__"` by hand: does it start with `__`? Does it end with `__`?
