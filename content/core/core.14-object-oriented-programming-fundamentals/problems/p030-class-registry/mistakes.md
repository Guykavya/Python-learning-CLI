- Forgetting `return klass` in the decorator. The class is registered, but the name `CsvExporter`
  becomes `None` in the module.
- Writing `register(cls, klass, name)` and trying to use it as `@Exporter.register("csv")`.
  A decorator with arguments needs two levels: the outer call takes the name, the inner function
  takes the class.
- Storing an object (`registry[name] = klass()`) instead of the class. Then every `create` returns
  the same shared object, and options like `sep=";"` cannot be passed.
- Creating `self.registry = {}` in an `__init__`. The registry must exist before any object does.
- Raising `KeyError(name)` with no hint. The user then sees only `'xml'` and has to guess the
  valid names.
- Checking for duplicates after storing the class. The old class is already replaced when the
  error is raised.
