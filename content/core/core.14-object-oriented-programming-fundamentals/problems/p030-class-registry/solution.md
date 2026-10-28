## Approach

**A shared class attribute on purpose.** Section 5 warns that a mutable class attribute is shared by
every object. Here that sharing is the goal: there must be exactly **one** registry for the whole
program, so it lives on `Exporter` as `registry = {}`.

**A decorator factory as a classmethod.** `Exporter.register("csv")` runs first and returns
`decorator`. Python then calls `decorator(CsvExporter)` and binds the name `CsvExporter` to the
result. So the decorator must return the class. While doing that, it records the class in the
registry and adds `format_name` to it (section 6 and the decorators chapter).

**A factory.** `create(name, **options)` turns a text name into an object of the right class. The
calling code never names a concrete class; new plug-ins only need the decorator line. This is
"open for extension": adding a format does not touch `create`.

The code writes `Exporter.registry`, not `cls.registry`. Both find the same dict here (a subclass
has no `registry` of its own, so lookup goes up to `Exporter`), but naming `Exporter` makes it
obvious that there is only one.

## Code

```python
import json


class Exporter:
    registry = {}

    @classmethod
    def register(cls, name):
        def decorator(klass):
            if not (isinstance(klass, type) and issubclass(klass, Exporter)):
                raise TypeError(f"{klass!r} is not an Exporter subclass")
            if name in Exporter.registry:
                raise ValueError(f"format {name!r} is already registered")
            Exporter.registry[name] = klass
            klass.format_name = name
            return klass
        return decorator

    @classmethod
    def create(cls, name, **options):
        if name not in Exporter.registry:
            known = ", ".join(sorted(Exporter.registry))
            raise KeyError(f"unknown format {name!r} (known: {known})")
        return Exporter.registry[name](**options)

    @classmethod
    def formats(cls):
        return sorted(Exporter.registry)

    def export(self, rows):
        raise NotImplementedError(f"{type(self).__name__} must define export()")


@Exporter.register("csv")
class CsvExporter(Exporter):
    def __init__(self, sep=","):
        self.sep = sep

    def export(self, rows):
        if not rows:
            return ""
        lines = [self.sep.join(rows[0])]
        for row in rows:
            lines.append(self.sep.join(str(value) for value in row.values()))
        return "\n".join(lines)


@Exporter.register("json")
class JsonExporter(Exporter):
    def __init__(self, indent=None):
        self.indent = indent

    def export(self, rows):
        return json.dumps(rows, indent=self.indent)
```

`self.sep.join(rows[0])` works because looping over a dict gives its keys.

## Complexity

`register`, `create` are O(1) (plus O(k log k) to build the error message for k formats).
`formats()` is O(k log k). `export` is O(total number of values).

## Another way

Python can register subclasses automatically: a base class may define the special classmethod
`__init_subclass__(cls, **kwargs)`, which runs every time a subclass is created, e.g.
`class CsvExporter(Exporter, format_name="csv")`. That is a later topic. The explicit decorator is
easier to read and lets a class decide whether it wants to be registered at all.
