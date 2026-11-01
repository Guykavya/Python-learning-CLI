# Factory and alternative constructors

Two small creation problems in one file.

**1. The exporter factory.** `create_exporter(fmt)` in `starter.py` is an `if/elif` chain. Adding
a format means editing the function, and the error says only `bad format`. Replace it with a
**registry**:

- `register_exporter(fmt)` is a decorator. `@register_exporter("json")` above a class stores it
  under the name `"json"` and returns the class unchanged.
- `create_exporter(fmt)` looks the class up and returns a **new instance** (`cls()`).
- An unknown name raises `ValueError`. The message names the bad format and lists the known
  ones sorted, for example: `unknown format 'xml'; known formats: csv, json`.
- `create_exporter` contains at most one `if` (the tests check it has no chain).
- Register `JsonExporter` as `"json"` and `CsvExporter` as `"csv"`; keep their `export` methods unchanged.

The tests register a brand-new exporter from the test file and expect `create_exporter` to find
it without any edit to your module.

**2. Alternative constructors.** `Money` is a frozen dataclass with `cents` and `currency`. The
loose function `parse_money(text)` builds one from text. Turn it into class methods:

- `Money.from_string("12.50 EUR")` is `Money(1250, "EUR")`. The currency is optional and
  defaults to `"USD"`; `"3"` is `Money(300)`; `"7.5"` means 7.50.
  (Only non-negative amounts, at most 2 decimals.)
- `Money.from_dict({"cents": 305, "currency": "GBP"})`. `currency` is optional.
- Both must work for **subclasses**: `Euro.from_string(...)` returns a `Euro`.

You may delete `parse_money`.

**Example**

```python
create_exporter("csv").export([{"name": "Ana", "score": 90}])   # 'name,score\nAna,90'
create_exporter("xml")      # ValueError: unknown format 'xml'; known formats: csv, json
Money.from_string("12.50 EUR")                                  # Money(cents=1250, currency='EUR')
```
