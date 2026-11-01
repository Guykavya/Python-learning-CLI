## Hint 1

Split the job by *when* each part runs:

- At class creation (`InterfaceMeta.__new__`): take the `abstract` keyword out of the keywords
  (a named parameter `abstract=False` does that), create the class with the remaining keywords,
  remember the flag **on this class only**, and check the requirements if it is concrete.
- At instance creation (`InterfaceMeta.__call__`): refuse abstract classes, otherwise call `super().__call__`.
- When someone reads `Shape.is_abstract` or `Shape.requirements`: properties defined on the metaclass.

Why can the flag not be read back with a plain `cls._abstract` lookup? What would `Triangle._abstract` find if `Triangle` did not set its own?

## Hint 2

```
class InterfaceMeta(type):
    def __new__(mcls, name, bases, ns, abstract=False, **kwargs):
        cls = super().__new__(mcls, name, bases, ns, **kwargs)   # kwargs go on to __init_subclass__
        cls._abstract = abstract
        if not abstract:
            missing = [r for r in cls.requirements if not implemented(cls, r)]
            if missing: raise TypeError(f"{name} must implement: " + ", ".join(sorted(missing)))
        return cls

    def __init__(cls, name, bases, ns, abstract=False, **kwargs):   # also receives the keyword
        super().__init__(name, bases, ns, **kwargs)

    is_abstract  (property): vars(cls).get("_abstract", False)
    requirements (property): union of vars(k).get("required", ()) for k in cls.__mro__, sorted tuple
    __call__: if abstract -> TypeError(f"{cls.__name__} is abstract"); else super().__call__(...)

implemented(cls, name):
    for k in cls.__mro__:
        if name in vars(k): return vars(k)[name] is not None
    return False
```
