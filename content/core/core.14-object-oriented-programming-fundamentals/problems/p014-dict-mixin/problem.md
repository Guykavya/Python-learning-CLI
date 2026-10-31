# A `to_dict` mixin for unrelated classes

A **mixin** is a small class that adds one behaviour and nothing else: no `__init__`, no data of its
own. Any class can "mix it in" by listing it as a base. A student and a product have nothing in
common, but both may need to be turned into a dict (to save as JSON, for example).

Write in `solution.py`:

- `ToDictMixin` with one method, `to_dict()`. It returns a **new** dict of the object's own
  attributes (`vars(self)`), but **skips every name that starts with `_`** (internal attributes).
  The mixin has no `__init__`.
- `Student(ToDictMixin)`: `Student(name, roll)` stores `name` and `roll`, and also
  `self._notes = []` (internal).
- `Product(ToDictMixin)`: `Product(sku, price)` stores `sku` and `price`, and also
  `self._discount = 0` (internal).

Changing the returned dict must not change the object.

**Example**

```python
s = Student("Kavya", 17)
print(s.to_dict())        # {'name': 'Kavya', 'roll': 17}
p = Product("PEN-01", 20)
print(p.to_dict())        # {'sku': 'PEN-01', 'price': 20}
s.city = "Pune"           # added later
print(s.to_dict())        # {'name': 'Kavya', 'roll': 17, 'city': 'Pune'}
```
