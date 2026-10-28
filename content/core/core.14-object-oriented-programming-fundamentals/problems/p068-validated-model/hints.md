## Hint 1

Start with the fields; they do not need `Model` at all. Each subclass handles `None` by calling
`super().check(name, value)` and returning that, so the "missing / default / required" logic is written
only once, in `Field`. Why must `IntField.__init__` accept `**kwargs` and pass them to
`super().__init__(**kwargs)`?

## Hint 2

For `fields()`: `vars(User)` holds `name`, `age` and `role` (plus other things you must skip with
`isinstance(value, Field)`). For `Admin`, you also need `User`'s fields. If you walk the MRO from
`object` up to `Admin` (`reversed(cls.__mro__)`) and write each field into one dict, what happens when
`Admin` writes `role` again? Where does `role` end up in the dict's order?

## Hint 3

```text
fields(cls):                      # @classmethod
    result = {}
    for klass in reversed(cls.__mro__):
        for name, value in vars(klass).items():
            if value is a Field: result[name] = value
    return result

validate(self):
    cleaned, errors = {}, []
    for name, field in self.fields().items():
        try: cleaned[name] = field.check(name, getattr(self, name))
        except FieldError as err: errors.append(err)
    if errors: raise ExceptionGroup(f"{type(self).__name__} has {len(errors)} invalid field(s)", errors)
    for name, value in cleaned.items(): setattr(self, name, value)
    return self
```
