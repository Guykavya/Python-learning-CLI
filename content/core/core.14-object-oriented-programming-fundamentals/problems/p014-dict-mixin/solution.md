## Approach

A mixin holds one piece of behaviour that unrelated classes can share (chapter section 13). It uses
only `self`, never a particular class, so it works wherever it is mixed in.

`vars(self)` is the object's real attribute dict (section 9). Returning it directly would let the
caller change the object by accident, so build a new dict with a comprehension and leave out the
names that start with `_`. That also skips mangled names like `_Thing__hidden` (section 7).

## Code

```python
class ToDictMixin:
    def to_dict(self):
        return {name: value for name, value in vars(self).items() if not name.startswith("_")}


class Student(ToDictMixin):
    def __init__(self, name, roll):
        self.name = name
        self.roll = roll
        self._notes = []


class Product(ToDictMixin):
    def __init__(self, sku, price):
        self.sku = sku
        self.price = price
        self._discount = 0
```

## Complexity

O(a) for an object with a attributes.

## Another way

`json.dumps(obj.to_dict())` turns the result into JSON text. Mixins are usually listed **before** the
main base class (`class Thing(ToDictMixin, Base)`), so their methods win if a name clashes; here there
is no clash, so either order works. In core.15 you will meet `dataclasses.asdict`, which does this for
dataclasses.
