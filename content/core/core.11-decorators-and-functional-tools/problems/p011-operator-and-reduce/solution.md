## Approach

`itemgetter(i)` builds the small "pick field i" function you would otherwise write as `lambda t: t[i]`.
With several keys it returns a tuple, and tuples compare item by item, so the second field breaks ties of
the first. `sorted` is stable, so items with equal keys keep their input order.

`reduce(f, seq, start)` carries one value along the list. For a product the start is 1. For `largest` there
is no safe start value, so use the first item (no start argument) and check for the empty list first.

## Code

```python
from functools import reduce
from operator import itemgetter, mul


def sort_by_price(items):
    return sorted(items, key=itemgetter(1))


def sort_people(people):
    return sorted(people, key=itemgetter("city", "age"))


def product(nums):
    return reduce(mul, nums, 1)


def largest(nums):
    if not nums:
        raise ValueError("largest() of an empty list")
    return reduce(lambda best, x: x if x > best else best, nums)
```

## Complexity

The sorts are O(n log n). `product` and `largest` are O(n).

## Another way

`math.prod(nums)` and `max(nums)` are the built-in answers, and in real code you should use them. `reduce`
is worth knowing for folds that have no built-in, such as merging a list of dicts.
