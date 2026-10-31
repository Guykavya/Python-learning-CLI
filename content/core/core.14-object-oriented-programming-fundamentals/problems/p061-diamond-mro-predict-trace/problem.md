# Trace: predict the MRO of a diamond with a mixin

This is the trace assessment of the module. It checks the outcome "predict the MRO in a diamond
inheritance". You need the C3 rule from chapter section 12, and the fact that `super()` means "the
**next class in the MRO of the object**", not "my parent".

```text
                 Base
                /    \
   LogMixin  Left    Right        (LogMixin has no parent except object)
       \       |      /
        +--- Bottom --+           Bottom(LogMixin, Left, Right)

   Other(Right, Left)             the same two classes, in the other order
```

Trace this program and write its output in `answer.txt`.

```python
class Base:
    def __init__(self):
        print("Base init")

    def hello(self):
        return ["Base"]


class LogMixin:
    def hello(self):
        return ["Log"] + super().hello()


class Left(Base):
    def __init__(self):
        print("Left init start")
        super().__init__()
        print("Left init end")

    def hello(self):
        return ["Left"] + super().hello()


class Right(Base):
    def __init__(self):
        print("Right init start")
        super().__init__()
        print("Right init end")

    def hello(self):
        return ["Right"] + super().hello()


class Bottom(LogMixin, Left, Right):
    def __init__(self):
        print("Bottom init start")
        super().__init__()
        print("Bottom init end")

    def hello(self):
        return ["Bottom"] + super().hello()


class Other(Right, Left):
    pass


b = Bottom()
print(b.hello())
print([c.__name__ for c in Bottom.__mro__])
print(Left.hello(b))
print(Left().hello())
o = Other()
print(o.hello())

try:
    class Broken(Left, Bottom):
        pass
except TypeError:
    print("Broken: no consistent MRO")

try:
    class Mixed(Bottom, Other):
        pass
except TypeError:
    print("Mixed: no consistent MRO")
```

Facts you need:

- `super().method()` inside class `K`, called on object `obj`, looks for `method` in the classes that
  come **after** `K` in `type(obj).__mro__`, and uses the first one that defines it.
- A class without its own `__init__` simply has none in its namespace; the search goes on to the next
  class in the MRO.
- `Left.hello(b)` calls the function defined in `Left` with `self = b`. Inside it, `super()` still
  uses `type(b).__mro__`.
- If C3 cannot find a consistent order, the `class` statement raises `TypeError`.

## Example of the format

```python
class A:
    def f(self):
        return ["A"]

class B(A):
    def f(self):
        return ["B"] + super().f()

print(B().f(), [c.__name__ for c in B.__mro__])
```

prints

```text
['B', 'A'] ['B', 'A', 'object']
```
