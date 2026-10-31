# First n valid sensor readings

A temperature sensor uploads its readings in several batches (lists, or generators that
download data). Some readings are broken: `None` when the sensor missed a reading, or values
outside the sensor's range of **0 to 50** (both ends allowed).

Write `first_valid(sources, n)` in `solution.py`. `sources` is a list of iterables. Treat them
as **one long stream**, in order, and return a **list** of the first `n` valid readings.
If there are fewer, return all valid ones.

Downloading a batch is slow, so: **do not read from a later source once you have `n` readings.**
The tests give you a source that fails the test if you touch it too early.

**Example**

```python
batches = [[12, None, 55, 20], [-3, 18], [25, 30]]
first_valid(batches, 3)    # [12, 20, 18]   the third list is never read
first_valid(batches, 10)   # [12, 20, 18, 25, 30]
first_valid(batches, 0)    # []
```
