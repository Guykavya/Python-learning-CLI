## Hint 1

`__init_subclass__(cls, ...)` is called on the parent **with the new subclass as `cls`**,
right after the class object is built. So you can inspect `cls.table` and `cls.fields` there.
Which check sees inherited attributes too: `"table" in cls.__dict__` or `hasattr(cls, "table")`?
Where do class keywords like `abstract=True` or `tag="x"` arrive?

## Hint 2

```
def __init_subclass__(cls, /, abstract=False, **kwargs):
    super().__init_subclass__(**kwargs)     # pass the rest on, always
    if abstract: return
    missing = sorted(names in ("table", "fields") that cls does not have)
    if missing: raise TypeError(f"{cls.__name__} is missing class attribute(s): {', '.join(missing)}")
    check table: str and not empty
    check fields: tuple, not empty, all str, len(set(fields)) == len(fields)

__init__(**values):  missing = fields not in values; unknown = values not in fields; setattr each
__repr__:            ", ".join(f"{f}={getattr(self, f)!r}" for f in self.fields)
```
