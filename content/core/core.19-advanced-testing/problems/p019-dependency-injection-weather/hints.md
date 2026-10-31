## Hint 1

Where does the class get its client from? If the answer is "it makes one", you cannot test it without
the real thing. What should `__init__` do with the argument?

## Hint 2

Write `line` first: ask the client once, then decide the label from the number. The `KeyError` case
needs `try` / `except`. Then `lines` is a loop (or comprehension) over `line`.

## Hint 3

```
__init__: self.client = client
line(city): try temp = self.client.temperature(city)
            except KeyError: return f"{city}: no data"
            label = "hot" if temp >= 30 else "cold" if temp <= 5 else "mild"
            return f"{city}: {temp}C, {label}"
lines(cities): [self.line(c) for c in cities]
```
