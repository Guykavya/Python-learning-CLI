## Approach

The constructor stores whatever client it is given. In production you pass a real HTTP client; in tests
you pass a tiny fake class that returns canned numbers. Nothing is patched, nothing is imported from the
network, and the test shows exactly what the class needs from its client (`temperature(city)` and
`KeyError`). That list is the **interface** of the dependency.

## Code

```python
class WeatherReport:
    def __init__(self, client):
        self.client = client

    def line(self, city):
        try:
            temp = self.client.temperature(city)
        except KeyError:
            return f"{city}: no data"
        if temp >= 30:
            label = "hot"
        elif temp <= 5:
            label = "cold"
        else:
            label = "mild"
        return f"{city}: {temp}C, {label}"

    def lines(self, cities):
        return [self.line(city) for city in cities]
```

## Complexity

`line` is O(1) plus one client call; `lines` is O(n) client calls for n cities.

## Another way

Accept a plain function instead of an object (`WeatherReport(get_temp)`). Functions are the lightest
possible seam in Python.
