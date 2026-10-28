## Approach

Name mangling (chapter section 7) is a simple text rewrite done by the compiler while it reads a class
body. It exists to avoid **accidental name clashes** between a class and its subclasses, not to hide
data. The rules:

- only names with two leading underscores are candidates,
- names that also end with two underscores are "special" (dunders) and keep their name,
- the class name loses its leading underscores, and an all-underscore class name switches mangling off,
- the result is `_` + class name + original name.

## Code

```python
def mangle(class_name, attr):
    for text in (class_name, attr):
        if not text.isidentifier():
            raise ValueError(f"not an identifier: {text!r}")
    if not attr.startswith("__") or attr.endswith("__"):
        return attr
    stripped = class_name.lstrip("_")
    if stripped == "":
        return attr
    return "_" + stripped + attr
```

`"__".startswith("__")` and `"__".endswith("__")` are both `True`, so `"__"` is returned unchanged by
the dunder rule.

## Complexity

O(n) in the length of the names (the string methods scan them once).

## Another way

Let Python do it, which is exactly what the tests do: `exec(f"class {c}:\n    {a} = 1")` and read
`vars()` of the new class. That is a good way to explore rules you are not sure about, but never use
`exec` on text you did not write yourself. In normal code you never need `mangle`: you only need to
know that `obj.__pin` written **outside** the class is not renamed, which is why it raises
`AttributeError` there, while `obj._Account__pin` works.
