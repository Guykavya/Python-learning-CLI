## Hint 1

Which parts are the same for every validator (finding the name, storing, reading, class
access), and which part changes (the check)? Put the same parts in `Validator`. In `__set__`,
in which order must "check" and "store" happen so that a bad value never replaces a good one?
How does `abc` stop someone from creating a `Validator` that has no check?

## Hint 2

```
class Validator(ABC):
    __set_name__: self.name = name
    __get__:      instance None -> self; else instance.__dict__[self.name] or AttributeError
    __set__:      self.validate(value); then instance.__dict__[self.name] = value
    @abstractmethod validate(value)

class Range(Validator):
    validate: if bool or not (int or float): TypeError
              if min set and value < min: ValueError(f"{self.name} must be >= {min}, got {value}")
              if max set and value > max: ValueError(...)
```

For `OneOf`, build the list of options with `", ".join(repr(o) for o in self.options)`.
