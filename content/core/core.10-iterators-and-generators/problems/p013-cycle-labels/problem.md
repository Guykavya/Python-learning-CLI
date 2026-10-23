# cycle_labels: repeat a pattern

Write `cycle_labels(labels, n)` in `solution.py`. It returns a list of length `n`: the items of `labels`
repeated over and over, in order, until there are `n` of them. Use `itertools.cycle` and `islice`.

**Examples**

```python
cycle_labels(["red", "green", "blue"], 7)
# ["red", "green", "blue", "red", "green", "blue", "red"]
cycle_labels(["a"], 3)      # ["a", "a", "a"]
cycle_labels(["a", "b"], 0) # []
cycle_labels([], 5)         # []
```
