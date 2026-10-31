# Dependency injection beats patching

Patching works, but the best seam is the one you design: **pass the dependency in**. A class that
receives its client in `__init__` can be tested with any fake object, with no `patch` at all.

In `solution.py` write the class `WeatherReport`:

```python
class WeatherReport:
    def __init__(self, client): ...
    def line(self, city): ...      # one line of text for one city
    def lines(self, cities): ...   # list of lines, in the order of `cities`
```

The client is any object with a method `temperature(city)` that returns the temperature in Celsius
(an `int` or `float`) and raises `KeyError` for a city it does not know. **Your class must never
create a client or import a network library itself.**

`line(city)` returns:

- `"Delhi: 35C, hot"` when the temperature is 30 or more,
- `"Oslo: 5C, cold"` when it is 5 or less,
- `"Pune: 21.5C, mild"` otherwise (the number is printed as the client gave it),
- `"Atlantis: no data"` when the client raises `KeyError`.

The client must be asked **once** per city per `line` call.

**Example**

```python
class FakeClient:
    def temperature(self, city):
        return {"Delhi": 35}[city]

WeatherReport(FakeClient()).line("Delhi")   # 'Delhi: 35C, hot'
```
