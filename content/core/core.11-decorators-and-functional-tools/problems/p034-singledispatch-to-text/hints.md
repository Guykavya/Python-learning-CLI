## Hint 1

The function decorated with `@singledispatch` is the **fallback**: it runs for types nobody
registered. What should it do here? Then add one `@to_text.register(SomeType)` function per row
of the table. Which row is the trap?

## Hint 2

For list, tuple and dict, call `to_text` itself on the parts: dispatch picks the right function
for each part. For a tuple, add a trailing comma when `len(value) == 1`. For `None`, register
`type(None)`.

## Hint 3

```
@singledispatch
to_text(value): raise TypeError(f"cannot convert {type(value).__name__}")

register int   -> str(value)
register bool  -> "yes" / "no"
register float -> f"{value:.2f}"
register str   -> '"' + value + '"'
register type(None) -> "null"
register list  -> "[" + ", ".join(to_text(x) for x in value) + "]"
register tuple -> same with ( ), plus "," if one item
register dict  -> "{" + ", ".join(f"{to_text(k)}: {to_text(v)}") + "}"
```
