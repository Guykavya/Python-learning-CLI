# A registry of exporter classes

A reporting tool can save data as CSV or JSON, and plug-ins add more formats later. Instead of a
long `if format == "csv": ... elif ...`, each exporter class **registers itself** under a name,
and the tool creates the right one from that name. Write it in `solution.py`.

**`Exporter`**, the base class:

- A class attribute `registry`, a dict from format name to exporter **class**.
- A classmethod `register(name)` that returns a **class decorator**. Used like this:

  ```python
  @Exporter.register("csv")
  class CsvExporter(Exporter):
      ...
  ```

  The decorator stores the class in `Exporter.registry[name]`, sets the class attribute
  `format_name = name` on that class, and returns the class unchanged. A name that is already
  registered raises `ValueError`. A class that is not a subclass of `Exporter` raises `TypeError`.
  In both error cases the registry is not changed.
- A classmethod `create(name, **options)` that finds the class and returns `cls_found(**options)`.
  An unknown name raises `KeyError` whose message contains the unknown name **and** the known names
  sorted and joined with `", "`, for example `unknown format 'xml' (known: csv, json)`.
- A classmethod `formats()` that returns the sorted list of registered names.
- A method `export(rows)` that raises `NotImplementedError`.

**Two exporters**, both registered with the decorator. `rows` is a list of dicts that all have
the same keys in the same order.

- `CsvExporter(sep=",")`, name `"csv"`. `export(rows)` returns the header line (the keys of the
  first row) and then one line per row, the values turned into `str` and joined with `sep`; lines
  are joined with `"\n"`. No rows gives `""`.
- `JsonExporter(indent=None)`, name `"json"`. `export(rows)` returns `json.dumps(rows, indent=indent)`.

**Example**

```python
rows = [{"name": "pen", "qty": 3}, {"name": "ink", "qty": 1}]
Exporter.formats()                       # ['csv', 'json']
Exporter.create("csv").export(rows)      # 'name,qty\npen,3\nink,1'
Exporter.create("csv", sep=";").export(rows)   # 'name;qty\npen;3\nink;1'
Exporter.create("json").export(rows[:1]) # '[{"name": "pen", "qty": 3}]'
CsvExporter.format_name                  # 'csv'
Exporter.create("xml")    # KeyError: "unknown format 'xml' (known: csv, json)"
```
