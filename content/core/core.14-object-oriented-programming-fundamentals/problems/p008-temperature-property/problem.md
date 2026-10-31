# Temperature with validated and computed properties

Nothing can be colder than absolute zero, −273.15 °C. A `Temperature` object should refuse such a
value, even when someone writes `t.celsius = -500` directly. A **property** lets you run code
when an attribute is read or written, while users still use plain attribute syntax.

Write a class `Temperature` in `solution.py`:

- `Temperature(celsius=0)` makes a temperature. It must use the same check as the setter below.
- `t.celsius` is a **property**. Reading it gives the temperature in °C. Setting it to a value below
  `-273.15` raises `ValueError("below absolute zero")` and keeps the old value. Store the real number
  in a backing attribute `self._celsius`.
- `t.fahrenheit` is a **computed property**: reading it returns `celsius * 9 / 5 + 32`. Setting it
  converts back, `(f - 32) * 5 / 9`, and stores that as the new celsius, with the same check.
  Do **not** store a separate Fahrenheit value.

**Example**

```python
t = Temperature(25)
print(t.celsius)         # 25
print(t.fahrenheit)      # 77.0
t.fahrenheit = 212
print(t.celsius)         # 100.0
t.celsius = -300         # ValueError: below absolute zero
print(t.celsius)         # 100.0  (unchanged)
Temperature(-274)        # ValueError: below absolute zero
```
