## Approach

Three moments, three metaclass hooks:

1. **Class creation**, `__new__`. The `abstract` keyword arrives here (and at `__prepare__` and
   `__init__`). Naming it as a parameter removes it from `**kwargs`, so it never reaches
   `type.__new__` (which would pass it to `object.__init_subclass__`, which accepts no keywords).
   After `super().__new__` the class exists, so we can walk its MRO and check the requirements.
2. **Instance creation**, `__call__`. `Shape()` is `type(Shape).__call__(Shape)`. We refuse
   abstract classes and delegate the rest to `type.__call__`, which runs `__new__` and `__init__`.
3. **Reading class information**: properties on the metaclass. A property defined on the
   metaclass works for `Shape.is_abstract` (the class is an *instance* of the metaclass) but not
   for `Shape().is_abstract`: instance lookup searches `type(obj).__mro__`, and the metaclass is not in it.

The abstract flag is stored on each class and read with `vars(cls)`, so a subclass never
inherits the parent's flag.

## Code

```python
class InterfaceMeta(type):
    def __new__(mcls, name, bases, ns, abstract=False, **kwargs):
        cls = super().__new__(mcls, name, bases, ns, **kwargs)
        cls._abstract = abstract                 # stored on this class only
        if not abstract:
            missing = [req for req in cls.requirements if not _implemented(cls, req)]
            if missing:
                raise TypeError(f"{name} must implement: {', '.join(sorted(missing))}")
        return cls

    def __init__(cls, name, bases, ns, abstract=False, **kwargs):
        super().__init__(name, bases, ns, **kwargs)

    @property
    def is_abstract(cls):
        return vars(cls).get("_abstract", False)

    @property
    def requirements(cls):
        names = set()
        for klass in cls.__mro__:
            names.update(vars(klass).get("required", ()))
        return tuple(sorted(names))

    def __call__(cls, *args, **kwargs):
        if cls.is_abstract:
            raise TypeError(f"{cls.__name__} is abstract")
        return super().__call__(*args, **kwargs)


def _implemented(cls, name):
    for klass in cls.__mro__:
        if name in vars(klass):
            return vars(klass)[name] is not None
    return False
```

`_implemented` copies what normal lookup does (the first class with the name wins) but reads the
raw dict values, so no descriptor runs and `area = None` correctly shadows a parent's method.

## Complexity

For a class with r requirements and an MRO of length m, the check is O(r × m) dict lookups,
done once per class statement. Instance creation adds one dict lookup.

## Another way

Do the check in the metaclass `__init__` (the class is complete there too) and keep the abstract
classes in a module-level set instead of an attribute:

```python
_ABSTRACT = set()

class InterfaceMeta(type):
    def __new__(mcls, name, bases, ns, abstract=False, **kwargs):
        return super().__new__(mcls, name, bases, ns, **kwargs)

    def __init__(cls, name, bases, ns, abstract=False, **kwargs):
        super().__init__(name, bases, ns, **kwargs)
        if abstract:
            _ABSTRACT.add(cls)
            return
        ...  # same check
```

Compare with the lighter tool: `__init_subclass__(cls, /, abstract=False, **kw)` on a base class
can do the class-creation check too. What it cannot do is refuse `Shape()` for the base class
itself and offer `Shape.is_abstract` without the attribute also appearing on instances: those
need the metaclass's `__call__` and properties. In real code, `abc.ABC` plus a test that
instantiates every concrete class is usually enough.
