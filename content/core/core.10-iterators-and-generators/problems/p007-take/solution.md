## Approach

Loop `n` times and pull one item per round. The `range(n)` loop stops after exactly `n` pulls, so the iterator is never asked for an extra item. `StopIteration` from a short input ends the loop early.

## Code

```python
def take(iterable, n):
    it = iter(iterable)
    result = []
    for _ in range(n):
        try:
            result.append(next(it))
        except StopIteration:
            break
    return result
```

## Complexity

O(n) time and memory.

## Another way

`list(itertools.islice(iterable, n))` does the same thing, and you will meet `islice` in the itertools section. Knowing the manual version shows you what `islice` does inside.
