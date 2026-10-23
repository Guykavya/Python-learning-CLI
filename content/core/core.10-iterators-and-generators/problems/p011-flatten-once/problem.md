# flatten_once with chain.from_iterable

Write `flatten_once(list_of_lists)` in `solution.py`. It takes an iterable of iterables, for example a
list of lists, and returns one **list** with all the items in order. Only one level is flattened.
Use `itertools.chain.from_iterable`.

**Examples**

```python
flatten_once([[1, 2], [3], [], [4, 5]])   # [1, 2, 3, 4, 5]
flatten_once(["ab", "cd"])                # ["a", "b", "c", "d"]
flatten_once([[1, [2]], [3]])             # [1, [2], 3]   (inner list stays)
flatten_once([])                          # []
```
