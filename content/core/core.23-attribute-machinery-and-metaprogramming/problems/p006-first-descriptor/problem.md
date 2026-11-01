# Your first descriptors

A **descriptor** is an object, stored as a class attribute, whose class defines `__get__`
(and optionally `__set__`). When you read `obj.attr` and `attr` on the class is a descriptor,
Python calls `descriptor.__get__(obj, type(obj))` and gives you its result. Reading the
attribute on the class itself (`Owner.attr`) calls `descriptor.__get__(None, Owner)`; the
convention is to return the descriptor itself then.

There is **one** descriptor object per class attribute, shared by all instances. So it must work
with the `instance` it is given, not keep per-object data on `self`.

Copy `starter.py` to `solution.py` and write two descriptor classes.

**`Upper(source)`**, a non-data descriptor (only `__get__`): reading it returns the attribute
named `source` of the instance, in upper case. It is computed on every read. Because it is
non-data, an instance attribute with the same name shadows it.

**`Fahrenheit()`**, a data descriptor (`__get__` and `__set__`) for a class that stores
`celsius`:

- reading gives `instance.celsius * 9 / 5 + 32`;
- assigning `F` sets `instance.celsius = (F - 32) * 5 / 9` and stores nothing else.

Both return the descriptor itself when accessed on the class.

**Example**

```python
class Person:
    shout = Upper("name")
    def __init__(self, name):
        self.name = name

class Temperature:
    fahrenheit = Fahrenheit()
    def __init__(self, celsius):
        self.celsius = celsius

Person("ada").shout       # 'ADA'
Person.shout              # <solution.Upper object at 0x...>   (address differs)
t = Temperature(100)
t.fahrenheit              # 212.0
t.fahrenheit = 32
t.celsius                 # 0.0
vars(t)                   # {'celsius': 0.0}
```
