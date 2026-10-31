## Hint 1

`isinstance(ElectricCar("X"), Car)` is `True`. So if your first check is "is it a `Car`?", what
happens to every electric car? In which order must the checks go?

## Hint 2

```
def category_of(item):
    if isinstance(item, ElectricCar): return "electric"
    if isinstance(item, Car):         return "car"
    if isinstance(item, Truck):       return "truck"
    if isinstance(item, Vehicle):     return "other vehicle"
    return "not a vehicle"

def count_by_category(items):
    counts = {name: 0 for name in the five names, in order}
    for item in items: counts[category_of(item)] += 1
    return counts
```
