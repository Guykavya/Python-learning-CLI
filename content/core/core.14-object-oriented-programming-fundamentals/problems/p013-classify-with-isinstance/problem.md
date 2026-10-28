# Classify vehicles with isinstance

`isinstance(obj, Cls)` is `True` when `obj` is a `Cls` **or an object of any subclass of `Cls`**.
An electric car *is a* car, and a car *is a* vehicle. That is why the order of your checks matters:
check the most specific class first.

`solution.py` already contains this small hierarchy (do not change it):

```python
class Vehicle:
    def __init__(self, plate):
        self.plate = plate


class Car(Vehicle):
    pass


class ElectricCar(Car):
    pass


class Truck(Vehicle):
    pass
```

Write two functions in `solution.py`:

- `category_of(item)` returns one of these strings:
  - `"electric"` for an `ElectricCar` (or a subclass of it),
  - `"car"` for any other `Car`,
  - `"truck"` for a `Truck`,
  - `"other vehicle"` for any other `Vehicle`,
  - `"not a vehicle"` for everything else (strings, numbers, `None`, ...).
- `count_by_category(items)` returns a dict with **all five** categories as keys, in the order above,
  and how many items fall in each category as values (0 if none).

**Example**

```python
items = [Car("KA01"), ElectricCar("KA02"), Truck("KA03"), Vehicle("KA04"), "bike", ElectricCar("KA05")]
print(category_of(items[1]))     # electric
print(count_by_category(items))
# {'electric': 2, 'car': 1, 'truck': 1, 'other vehicle': 1, 'not a vehicle': 1}
```
