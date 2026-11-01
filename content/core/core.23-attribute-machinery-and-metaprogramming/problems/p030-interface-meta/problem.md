# An interface checker metaclass

`abc.ABC` refuses to create an *instance* of a class that forgot to implement an abstract
method, but you only find out when somebody instantiates it. Build a stricter version: a
metaclass that refuses to create the **class itself**, so the mistake shows up as soon as the
module is imported.

Copy `starter.py` to `solution.py` and write the metaclass `InterfaceMeta`:

**Declaring requirements.** A class lists required names in a class attribute `required`
(a tuple of strings). The requirements of a class are the **union** of the `required` tuples found
in the own `__dict__` of every class in its MRO, so a subclass can add more requirements.

**Abstract classes.** A class created with the class keyword `abstract=True` is not checked:

```python
class Shape(metaclass=InterfaceMeta, abstract=True):
    required = ("area", "perimeter")
```

The keyword is **not inherited**: a subclass is concrete unless it also says `abstract=True`.
The metaclass must consume `abstract` itself; any other class keywords must still reach
`__init_subclass__` as usual.

**Checking concrete classes.** When a concrete class is created, every requirement must be
*implemented*: walking the new class's MRO, the **first** class that has the name in its own
`__dict__` (the one normal lookup would find) holds a value that is not `None`. Writing
`area = None` means "deliberately not implemented", even if a parent implements it. An
implementation inherited from a parent or a mixin counts. If anything is missing, raise
`TypeError` with exactly this message, names sorted:

```
Square must implement: area, perimeter
```

**On the class, not the instance.** Add to the metaclass:

- a property `is_abstract`: `True` for classes created with `abstract=True`, else `False`;
- a property `requirements`: the sorted tuple of all requirement names;
- a `__call__` that raises `TypeError("Shape is abstract")` when someone tries to instantiate an
  abstract class (concrete classes are created normally, `__init__` included).

Because these live on the metaclass, `Square.is_abstract` works but `Square(2).is_abstract`
raises `AttributeError`, as for any attribute of the metaclass.

**Example**

```python
class Shape(metaclass=InterfaceMeta, abstract=True):
    required = ("area", "perimeter")

class Square(Shape):
    def __init__(self, side):
        self.side = side
    def area(self):
        return self.side ** 2
    def perimeter(self):
        return 4 * self.side

Square(3).area()        # 9
Square.requirements     # ('area', 'perimeter')
Shape.is_abstract       # True
Shape()                 # TypeError: Shape is abstract

class Circle(Shape):    # TypeError: Circle must implement: area, perimeter
    pass
```
