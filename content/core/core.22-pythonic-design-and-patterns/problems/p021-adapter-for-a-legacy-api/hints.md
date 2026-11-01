## Hint 1

What does `monitor` actually call on the sensor? Only one method. So what is the smallest
object you can build that has that method and gets its data from the legacy object? Should it
inherit from the legacy class or just *hold* one?

## Hint 2

```
class FahrenheitAdapter:
    __init__(self, legacy): remember legacy
    celsius(self):
        text = legacy.read_fahrenheit_string()   # read again on EVERY call
        number = float(text without spaces and without the last letter)
        return (number - 32) * 5 / 9

adapt_function(read_f):
    return something with a celsius attribute that is a function:
        lambda: (read_f() - 32) * 5 / 9
```

`types.SimpleNamespace(celsius=...)` is a quick way to make "an object with a method".
`"72.5F".rstrip("Ff")` removes the unit letter.
