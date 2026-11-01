## Hint 1

`__set_name__(self, owner, name)` is called with `name` equal to `"title"` for `title = Field()`.
Where do you save it so `__get__` and `__set__` can use it later? Then: which dictionary belongs
to one book only? How do you read "the stored value or the default" from a dict in one call?

## Hint 2

```
__set_name__(owner, name):  self.name = name
__get__(instance, owner):
    if instance is None: return self
    return instance.__dict__.get(self.name, self.default)
__set__(instance, value):   instance.__dict__[self.name] = value
__delete__(instance):
    if self.name not in instance.__dict__: raise AttributeError(... self.name ...)
    remove instance.__dict__[self.name]
```

Why `instance.__dict__[...] = value` and not `setattr(instance, self.name, value)`? Try it and
see what `setattr` calls.
