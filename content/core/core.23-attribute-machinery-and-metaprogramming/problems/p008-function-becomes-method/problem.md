# How a function becomes a method

A `def` inside a class creates an ordinary function and stores it in the class `__dict__`.
Functions are **non-data descriptors**: they have a `__get__` method. So when you read
`acc.deposit`, Python finds the function on the class and calls
`Account.__dict__["deposit"].__get__(acc, Account)`, which returns a **bound method**: a small
object holding the function (`__func__`) and the instance (`__self__`). Calling it calls
`__func__(__self__, *args)`.

Copy `starter.py` to `solution.py` and write three functions:

- `bind(func, obj)`: return `func` bound to `obj`, the same kind of object `obj.func` would be if
  `func` were defined in `obj`'s class. Do **not** change `obj` or its class (some objects, with
  `__slots__`, cannot even take new attributes).
- `method_parts(method)`: return the tuple `(function, instance)` behind a bound method.
- `rebind(method, other)`: return a **new** bound method with the same function, bound to `other`.
  The original method is unchanged.

**Example**

```python
class Account:
    def __init__(self, balance):
        self.balance = balance
    def deposit(self, amount):
        self.balance += amount
        return self.balance

def describe(self):
    return f"I am a {type(self).__name__}"

a, b = Account(10), Account(100)
m = bind(describe, a)
m()                                  # 'I am a Account'
method_parts(a.deposit) == (Account.deposit, a)   # True
rebind(a.deposit, b)(1)              # 101  (b changed, a still 10)
```
