- Returning `self.celsius` inside the `celsius` getter. The getter calls itself until `RecursionError`.
- Writing `self._celsius = celsius` in `__init__`. The check is skipped, so `Temperature(-500)` works.
- Storing a separate `self._fahrenheit`. After `t.celsius = 30` the two values disagree.
- Using `<=` for the check. Exactly −273.15 is allowed; only colder values are not.
- Naming the setter function differently (`def set_celsius` under `@celsius.setter`). Both getter and
  setter must use the property's name.
- Writing `(value - 32) * 5 // 9`. Floor division throws away the fraction.
