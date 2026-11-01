# Instrument every method with a class decorator

You want to know which methods of a class are used, and how often, without editing every
method. A **class decorator** can do it: it receives the finished class, replaces each method
with a counting wrapper, and returns the class.

The hard part is that "a method" is stored in the class in different shapes. Look at
`vars(cls)` (the raw class dictionary), not at `getattr(cls, name)`:

| In `vars(cls)` | What `getattr(cls, name)` gives you |
|---|---|
| a plain function | the same function |
| a `classmethod` object | a **bound method** (already bound to `cls`) |
| a `staticmethod` object | the inner function, unwrapped |
| a `property` object | the property object |

If you wrap what `getattr` returns and store it back, classmethods and staticmethods break.

Copy `starter.py` to `solution.py` and write:

- `count_calls(cls)`: a class decorator that returns the **same** class after:
  - wrapping every plain function defined **in `cls` itself** (not inherited ones),
  - wrapping the function inside every `classmethod` and `staticmethod`, and storing a new
    `classmethod`/`staticmethod` around the wrapper, so they keep working the same way,
  - leaving alone: names that start **and** end with `__` (dunders such as `__init__`),
    properties, nested classes, plain data, and any other object,
  - creating `cls.call_counts`: a dict from each wrapped name to `0`, in definition order.
  Each call adds 1 to its method's count **before** the method runs (a call that raises still counts).
  Wrappers keep the method's `__name__` and `__doc__` (use `functools.wraps`).
- `reset_counts(cls)`: sets every count of `cls.call_counts` back to `0` (same keys).

**Example**

```python
@count_calls
class Account:
    rate = 0.05

    def __init__(self, balance):
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

    @classmethod
    def empty(cls):
        return cls(0)

    @staticmethod
    def fee(amount):
        return amount * 0.01

    @property
    def rich(self):
        return self.balance > 1000


a = Account.empty()        # counts: empty 1
a.deposit(10)
a.deposit(5)
Account.fee(100)           # works through the class
a.fee(100)                 # and through an instance (no self passed)
a.rich                     # not counted: properties are left alone
Account.call_counts        # {'deposit': 2, 'empty': 1, 'fee': 2}
```
