# Mean, median and mode from scratch

Chapter section 8. Write three functions **without** importing `statistics`:

- `mean(values)`: the sum divided by the count (a float).
- `median(values)`: the middle value of the sorted data; for an even count, the mean of the two middle values.
- `modes(values)`: a **sorted list** of every value that occurs most often (all tied values). If every value is unique, all values are tied.

An empty list raises `ValueError` whose message contains the word `empty`. None of the functions may change the caller's list.

## Example

```python
mean([2, 4, 9])            # 5.0
median([5, 1, 3])          # 3
median([4, 1, 3, 2])       # 2.5
modes([1, 2, 2, 3, 3, 4])  # [2, 3]
modes([7, 7, 1])           # [7]
```
