## Approach

`isinstance` answers "is this object a kind of X?", and it says yes for subclasses too (chapter
section 10). An `ElectricCar` passes `isinstance(x, ElectricCar)`, `isinstance(x, Car)` **and**
`isinstance(x, Vehicle)`. So test from the most specific class to the most general, and stop at the
first match.

`count_by_category` starts every category at 0 (so all keys exist, in order) and adds 1 for each
item's category.

## Code

```python
CATEGORIES = ["electric", "car", "truck", "other vehicle", "not a vehicle"]


def category_of(item):
    if isinstance(item, ElectricCar):
        return "electric"
    if isinstance(item, Car):
        return "car"
    if isinstance(item, Truck):
        return "truck"
    if isinstance(item, Vehicle):
        return "other vehicle"
    return "not a vehicle"


def count_by_category(items):
    counts = {name: 0 for name in CATEGORIES}
    for item in items:
        counts[category_of(item)] += 1
    return counts
```

## Complexity

O(n) for n items; each `isinstance` check is quick.

## Another way

`type(item) is Car` checks the exact class only. It would put a `SportsCar(Car)` in "not a vehicle",
which is why `isinstance` is usually right. Often the best design avoids type checks altogether:
give each class a `category` class attribute or method and just ask `item.category` (polymorphism,
section 15). Type checks are fine at the edges, like here, where some items are not vehicles at all.
