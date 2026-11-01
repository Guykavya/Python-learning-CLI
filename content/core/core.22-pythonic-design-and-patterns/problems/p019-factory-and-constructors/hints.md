## Hint 1

What would you need to store so that a name can find a class *without* an `if`? Where could
that store be filled in, so that each exporter class announces itself right where it is
defined? For `Money`: which decorator gives a method the class (not an instance) as first
argument, and how do you build an object from that class so subclasses work?

## Hint 2

```
EXPORTERS = {}

def register_exporter(fmt):
    def decorator(cls):
        EXPORTERS[fmt] = cls
        return cls
    return decorator

def create_exporter(fmt):
    try: cls = EXPORTERS[fmt]
    except KeyError: raise ValueError(message with sorted(EXPORTERS))
    return cls()

class Money:
    @classmethod
    def from_string(cls, text): ... return cls(cents, currency)
```

The cents of `"7.5"`: pad the fraction to two digits (`"5"` becomes `"50"`) before `int(...)`.
