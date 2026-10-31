## Hint 1

`@Exporter.register("csv")` above a class means: first call `Exporter.register("csv")`, which must
**return a function**; then Python calls that function with the class and binds the class name to
whatever it returns. So `register` is a decorator factory, like the ones with arguments in the
decorators chapter. What must the inner function return so that `CsvExporter` is still the class?

## Hint 2

The registry is one dict on the base class: `registry = {}` in the class body. A class attribute
is shared, which is exactly what you want here. To make an object from a class stored in a dict,
call the value: `Exporter.registry[name](**options)`. For the error message:
`", ".join(sorted(Exporter.registry))`.

## Hint 3

```
@classmethod
def register(cls, name):
    def decorator(klass):
        if klass is not a subclass of Exporter: raise TypeError
        if name already in Exporter.registry:  raise ValueError
        Exporter.registry[name] = klass
        klass.format_name = name
        return klass
    return decorator

@classmethod
def create(cls, name, **options):
    if name not in Exporter.registry:
        raise KeyError(f"unknown format {name!r} (known: {sorted names joined})")
    return Exporter.registry[name](**options)
```
