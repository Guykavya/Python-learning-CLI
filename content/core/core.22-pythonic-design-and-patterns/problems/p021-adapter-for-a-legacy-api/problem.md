# Adapter for a legacy API

Your new code is written against a small interface: any object with a method `celsius()` that
returns a float (see `monitor` in `starter.py`). But the hardware vendor's class,
`LegacyTemperatureSensor`, only offers `read_fahrenheit_string()`, which returns text like
`"72.5F"`. You may not edit the vendor class (it is shared by many projects).

An **adapter** is a thin wrapper that makes one interface look like another.

Copy `starter.py` to `solution.py`. Keep `LegacyTemperatureSensor` and `monitor` exactly as they
are, and write:

- `FahrenheitAdapter(legacy)`, whose `celsius()` calls `legacy.read_fahrenheit_string()` **every
  time**, parses the number (ignore whitespace, and accept `F` or `f` as the suffix) and returns
  degrees Celsius: `(F - 32) * 5 / 9`.
- `adapt_function(read_f)`: `read_f` is a function returning a Fahrenheit **float**. Return an
  object whose `celsius()` calls `read_f()` and converts. Keep it tiny (a closure or a lambda,
  not a new big class).

Rules: wrap, do not modify. Do not add methods to the legacy class or object, and do not
inherit from it.

**Example**

```python
legacy = LegacyTemperatureSensor(["72.5F", "95F"])
sensor = FahrenheitAdapter(legacy)
sensor.celsius()        # 22.5
monitor(sensor)         # 'ALERT 35.0C'   (the second reading, 95F)

fake = adapt_function(lambda: 50.0)
monitor(fake)           # 'ok 10.0C'
```
