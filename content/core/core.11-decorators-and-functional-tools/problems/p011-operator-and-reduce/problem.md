# itemgetter for sorting, reduce for folding

The `operator` module has ready-made functions for things you would otherwise write as a small `lambda`.
`functools.reduce` folds a sequence into one value.

Write four functions in `solution.py`. Do not change the input lists.

1. `sort_by_price(items)`: `items` is a list of `(name, price)` tuples. Return a new list sorted by price,
   lowest first. Items with the same price keep their original order. Use `operator.itemgetter(1)`.
2. `sort_people(people)`: `people` is a list of dicts with keys `"name"`, `"city"`, `"age"`. Return a new list
   sorted by city, and inside one city by age. Use `itemgetter("city", "age")`.
3. `product(nums)`: multiply all numbers with `reduce` and `operator.mul`. The product of an empty list is `1`.
4. `largest(nums)`: return the biggest number using `reduce` (not `max`). For an empty list raise
   `ValueError("largest() of an empty list")`.

**Examples**

```python
sort_by_price([("tea", 20), ("cake", 50), ("bun", 20)])
# [('tea', 20), ('bun', 20), ('cake', 50)]

sort_people([
    {"name": "Ann", "city": "Pune", "age": 30},
    {"name": "Bo",  "city": "Agra", "age": 41},
    {"name": "Cy",  "city": "Pune", "age": 25},
])
# Bo (Agra), then Cy (Pune, 25), then Ann (Pune, 30)

product([2, 3, 4])    # 24
product([])           # 1
largest([3, 9, 2])    # 9
```
