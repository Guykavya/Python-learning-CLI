# Fractional knapsack

A trader's bag holds at most `capacity` kilograms. Item `i` is a pile of spice with value `items[i][0]` and weight `items[i][1]`. Any **fraction** of a pile may be taken: half the pile weighs half and is worth half. Write `fractional_knapsack(items, capacity)` that returns the **largest total value** that fits, as a `float`.

Rules (chapter section 7):

- `items` is a list of `(value, weight)` pairs of integers with `value >= 0` and `weight > 0`. `capacity >= 0` is an integer.
- Return a `float`. The tests compare with `math.isclose`, so tiny rounding differences are fine.
- Do not change the list you are given.

## Example

```python
>>> fractional_knapsack([(60, 10), (100, 20), (120, 30)], 50)
240.0
>>> fractional_knapsack([(30, 5), (20, 10)], 8)
36.0
>>> fractional_knapsack([(10, 1), (50, 50), (1, 1)], 50)
59.0
>>> fractional_knapsack([(60, 10)], 0)
0.0
```

In the first example: all of the first two piles (densities 6 and 5), then `20/30` of the third, worth 80.

## Constraints

- `0 <= len(items) <= 10**5`. Aim for `O(n log n)`.

## Think about

Neither the value nor the weight alone is the right sort key (the third example breaks "highest value first"). What single number per item tells you how good one kilogram of it is?
