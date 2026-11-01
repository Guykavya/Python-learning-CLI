# Explain: the wrong tool for the job

After this chapter it is tempting to solve everything with metaclasses and `__getattr__`.
Your team lead asks you to review three pieces of code that a clever colleague wrote. Each one
works. Each one uses heavier magic than it needs.

**Snippet A: a metaclass that writes `__init__`, `__repr__` and `__eq__`**

```python
class RecordMeta(type):
    def __new__(mcls, name, bases, ns):
        fields = ns.get("fields", ())

        def __init__(self, *args):
            for field, value in zip(fields, args):
                setattr(self, field, value)

        def __repr__(self):
            inner = ", ".join(f"{f}={getattr(self, f)!r}" for f in fields)
            return f"{name}({inner})"

        def __eq__(self, other):
            return type(self) is type(other) and all(
                getattr(self, f) == getattr(other, f) for f in fields)

        ns.update(__init__=__init__, __repr__=__repr__, __eq__=__eq__)
        return super().__new__(mcls, name, bases, ns)


class Point(metaclass=RecordMeta):
    fields = ("x", "y")
```

**Snippet B: `__getattr__` that computes values**

```python
class Person:
    def __init__(self, first, last, birth_year):
        self.first, self.last, self.birth_year = first, last, birth_year

    def __getattr__(self, name):
        if name == "full_name":
            return f"{self.first} {self.last}"
        if name == "age":
            return 2026 - self.birth_year
        return None
```

**Snippet C: a metaclass that keeps a registry and checks a class attribute**

```python
EXPORTERS = {}


class ExporterMeta(type):
    def __init__(cls, name, bases, ns):
        super().__init__(name, bases, ns)
        if bases:                       # skip the base class itself
            if "extension" not in ns:
                raise TypeError(f"{name} must define extension")
            EXPORTERS[ns["extension"]] = cls


class Exporter(metaclass=ExporterMeta):
    def export(self, rows):
        raise NotImplementedError


class CsvExporter(Exporter):
    extension = "csv"

    def export(self, rows):
        return "\n".join(",".join(map(str, r)) for r in rows)
```

Write `answer.md` (about 350 to 500 words) with these parts:

1. **For each snippet (A, B, C)**: name the lighter tool you would use instead (choose from:
   `@dataclass`, `property`, `__init_subclass__`, a plain function or class decorator), show the
   key lines of the replacement, and give **two concrete costs** of the current version (bugs it
   hides, what a reader or a tool such as an IDE or type checker cannot see, surprises for users).
2. **One hidden bug**: Snippet B has a behaviour that will bite someone. Describe it with an example call.
3. **When is a metaclass justified?** Give one realistic case where none of the lighter tools is
   enough, and say which metaclass feature it needs.

**Example of the level of detail expected (a different snippet)**

> *A class with `__getattribute__` that logs every access, used only to debug one attribute.*
> Lighter tool: a `property` for that one attribute that logs in its getter. Costs: every
> access to every attribute (including `self.x` inside methods) pays for the hook, and a typo in
> the hook (forgetting `super().__getattribute__`) causes infinite recursion.
