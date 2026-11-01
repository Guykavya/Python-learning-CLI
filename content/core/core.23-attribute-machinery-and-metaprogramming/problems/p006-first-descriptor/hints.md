## Hint 1

What are the three arguments of `__get__(self, instance, owner)`? Which one is the `Person`
object whose name you need, and which one is the shared descriptor? What is `instance` when you
write `Person.shout`? To read "the attribute whose name is in a string", which built-in do you use?

## Hint 2

```
class Upper:
    __init__(source): remember source on self
    __get__(instance, owner):
        if instance is None: return self
        return getattr(instance, self.source).upper()

class Fahrenheit:
    __get__(instance, owner):
        if instance is None: return self
        return instance.celsius * 9 / 5 + 32
    __set__(instance, value):
        instance.celsius = (value - 32) * 5 / 9
```

Do not give `Upper` a `__set__`: that would make it a data descriptor and stop instance
attributes from shadowing it.
