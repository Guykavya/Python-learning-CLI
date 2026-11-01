# Class contracts with `__init_subclass__`

A base class often needs every subclass to fill in some class attributes. If one is
forgotten, the mistake normally shows up much later, deep inside some method, as a confusing
`AttributeError`. `__init_subclass__` runs **when the subclass is created** (at the `class`
statement), so the base class can check the contract right there and fail fast with a clear
message.

Copy `starter.py` to `solution.py` and write the base class `Record`:

**The contract** (checked in `__init_subclass__`, raising `TypeError` at class creation):

1. The subclass must have the class attributes `table` and `fields` (defined in its body or
   inherited from a parent). If any are missing, the message names the class and **every**
   missing attribute, for example `Broken is missing class attribute(s): fields, table`.
2. `table` must be a non-empty `str`.
3. `fields` must be a non-empty `tuple` of `str` with no duplicates.
4. `class Base(Record, abstract=True)` skips the check, for intermediate base classes. The
   flag is **not inherited**: a subclass of `Base` is checked again.
5. `__init_subclass__` must cooperate: accept extra keyword arguments and pass them on with
   `super().__init_subclass__(**kwargs)`, so `Record` can be combined with other bases that
   have their own `__init_subclass__`. An unknown class keyword must still end in `TypeError`
   (that is what `object.__init_subclass__` does with leftovers).

**What every record gets**

6. `__init__(self, **values)`: needs exactly the names in `fields`. A missing or unknown
   name raises `TypeError` naming it. Each value is stored as an instance attribute.
7. A `__repr__` like `User(id=1, name='Ann')`, in `fields` order, with `repr` of each value.
   A subclass that writes its own `__repr__` keeps it.

**Example**

```python
class User(Record):
    table = "users"
    fields = ("id", "name")

User(name="Ann", id=1)          # User(id=1, name='Ann')
User(id=1)                      # TypeError: User missing field(s): name

class Broken(Record):           # TypeError right here, at the class statement:
    pass                        # Broken is missing class attribute(s): fields, table

class Timestamped(Record, abstract=True):   # allowed: abstract
    pass

class Event(Timestamped):       # checked again: needs table and fields
    table = "events"
    fields = ("at", "what")
```
