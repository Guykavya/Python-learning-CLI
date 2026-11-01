# Trace: the order of class creation

A `class` statement is not a declaration. It is a piece of code that **runs**, step by step,
and several hooks get a turn while it runs. Below, every hook prints a line. Work out the full
output **without running it**, then check.

Facts you may need (not the answer):

- A decorator *expression* is evaluated before the class, but the decorator is *called* only
  after the class object exists.
- Keyword arguments in the class line (`class Point(Base, tag="p")`) are passed to the
  metaclass hooks, and `type.__new__` hands them on to `__init_subclass__`.
- `__set_name__` and `__init_subclass__` are both called **from inside** `type.__new__`, that is,
  during the `super().__new__(...)` call in the metaclass.
- `Point(1, 2)` calls `type(Point).__call__`, which is the metaclass's `__call__`.

```python
class Meta(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kw):
        print(f"1 prepare {name} {kw}")
        return {}

    def __new__(mcls, name, bases, ns, **kw):
        own = [k for k in ns if not k.startswith("__")]
        print(f"2 meta new {name} {own}")
        cls = super().__new__(mcls, name, bases, ns, **kw)
        print(f"3 meta new done {name}")
        return cls

    def __init__(cls, name, bases, ns, **kw):
        print(f"4 meta init {name}")
        super().__init__(name, bases, ns, **kw)

    def __call__(cls, *args):
        print(f"5 meta call {cls.__name__} {args}")
        obj = super().__call__(*args)
        print(f"6 meta call done {type(obj).__name__}")
        return obj


class Field:
    def __init__(self, label):
        self.label = label
        print(f"field {label}")

    def __set_name__(self, owner, name):
        print(f"set_name {owner.__name__}.{name} ({self.label})")


class Base(metaclass=Meta):
    def __init_subclass__(cls, **kw):
        print(f"init_subclass {cls.__name__} {kw}")
        super().__init_subclass__()


def deco(cls):
    print(f"decorate {cls.__name__}")
    return cls


print("--- define Point")


@deco
class Point(Base, tag="p"):
    print("body start")
    x = Field("first")
    y = Field("second")

    def __new__(cls, *args):
        print("Point new")
        return super().__new__(cls)

    def __init__(self, x, y):
        print(f"Point init {x} {y}")

    def norm(self):
        return 0

    print("body end")


print("--- make a Point")
p = Point(1, 2)
print("--- done", type(Point).__name__, type(p).__name__)
```

**Example**: the first line is printed while the class `Base` is created (before any line of
`Point` runs):

```
1 prepare Base {}
```

`Base` is created with the metaclass `Meta` too, so it goes through some of the same steps as
`Point`. Ask yourself which hooks fire for `Base` and which do not.

Write in `answer.txt` all the lines the program prints, in order (23 lines).
