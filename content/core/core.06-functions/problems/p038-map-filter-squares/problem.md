# Squares of the evens with map and filter

Write two functions, each using **both** `map` and `filter`:

1. `squares_of_evens(numbers)` returns a list of the squares of the even numbers, in order.
2. `parse_positive(text)` takes a line of whitespace-separated integers, such as
   `"4 -2 0 7"`, and returns a list of the **positive** ones as ints.

Both must return **lists**, not map or filter objects.

**Examples**

```python
squares_of_evens([1, 2, 3, 4, 5, 6])   # [4, 16, 36]
squares_of_evens([])                   # []
parse_positive("4 -2 0 7")             # [4, 7]
parse_positive("")                     # []
```
