## Hint 1

Three methods share the same index rules (negative numbers, range check, type check). Instead of writing them three times, what small helper method could turn any index into a valid non-negative one, or raise?

## Hint 2

The helper `_fix(index)`: `TypeError` if it is not an `int`; if negative, add `self._size`; `IndexError` unless `0 <= index < self._size`. For `__delitem__`, think about the dict: every key **greater** than the deleted index must become `key - 1`, and the key equal to it disappears.

## Hint 3

```
__getitem__(i):  return data.get(fix(i), default)
__setitem__(i, v): i = fix(i); if v == default: data.pop(i, None) else: data[i] = v
__delitem__(i):  i = fix(i); data = {k-1 if k > i else k: v for k, v in data.items() if k != i}; size -= 1
__iter__:        for i in range(size): yield data.get(i, default)
```
