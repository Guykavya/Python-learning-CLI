# Running median

Numbers arrive one at a time. After every number you must be able to say, at once, what the **median** of all numbers seen so far is. Write the class `MedianFinder`:

- `add(x)` takes in one more number `x` (an `int` or a `float`);
- `median()` returns the median of all numbers added so far:
  - for an **odd** count, the middle number of the sorted data (the number itself, not a copy turned into a float);
  - for an **even** count, the average of the two middle numbers, `(a + b) / 2`;
  - before any number has been added it raises `ValueError`.

The idea of section 8 of the chapter is a good fit: the lower half of the numbers in a max-heap, the upper half in a min-heap. `heapq` is allowed.

## Example

```python
>>> mf = MedianFinder()
>>> mf.add(5); mf.median()
5
>>> mf.add(2); mf.median()
3.5
>>> mf.add(8); mf.median()
5
>>> mf.add(1); mf.median()
3.5
>>> mf.add(9); mf.add(3); mf.median()     # data so far: 1 2 3 5 8 9
4.0
```

## Constraints

- Up to 100,000 numbers; `median()` is called after every `add`.
- The tests run this big case in a separate process with a 10-second limit. Sorting the data again on every call needs minutes.
- Values may repeat and may be negative.

## Think about

Why must the two halves differ in size by at most one? Which heap gets the extra number when the count is odd? When a new number arrives, how can you be sure it lands on the correct side of the middle without comparing it with both tops?
