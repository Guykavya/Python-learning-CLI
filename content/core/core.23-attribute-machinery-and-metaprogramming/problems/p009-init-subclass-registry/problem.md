# A plugin registry with `__init_subclass__`

When a class is created, Python calls `__init_subclass__` on its **parent** (as an implicit
classmethod, with the new class as `cls`). Keyword arguments written in the class header, like
`class CsvExporter(Plugin, key="csv")`, are passed to it. That is enough to build a plugin
registry without a metaclass and without a decorator on every plugin.

Copy `starter.py` to `solution.py` and finish the class `Plugin`:

- `Plugin.registry` is **one** dict shared by the whole hierarchy: key -> plugin class.
- `__init_subclass__(cls, /, key=None, **kwargs)`:
  - first passes any other keywords on with `super().__init_subclass__(**kwargs)`, so other
    bases in a multiple-inheritance hierarchy get theirs (and unknown keywords still fail with
    `TypeError`);
  - if `key` is `None`, does nothing more: the class is a helper base, not a plugin;
  - if `key` is already registered, raises `ValueError` naming the key, so the class statement
    fails and the first plugin stays registered;
  - otherwise stores `cls.key = key` and `Plugin.registry[key] = cls`.
- `Plugin.create(key, *args, **kwargs)` (a classmethod) looks the class up and returns
  `plugin_class(*args, **kwargs)`; an unknown key raises `KeyError` naming it.

**Example**

```python
class CsvExporter(Plugin, key="csv"):
    def __init__(self, sep=","):
        self.sep = sep

class JsonExporter(Plugin, key="json"):
    pass

Plugin.registry               # {'csv': <class 'CsvExporter'>, 'json': <class 'JsonExporter'>}
Plugin.create("csv", sep=";").sep   # ';'
class Again(Plugin, key="csv"):     # ValueError: duplicate plugin key 'csv' ...
    pass
```

(The real `repr` of a class also shows its module, for example `<class 'solution.CsvExporter'>`.)
