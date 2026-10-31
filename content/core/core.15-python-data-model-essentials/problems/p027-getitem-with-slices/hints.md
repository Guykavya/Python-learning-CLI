## Hint 1

What object does Python pass to `__getitem__` for `s[1:3]`? Print it inside the method to see. How can you tell it apart from an `int`?

## Hint 2

`isinstance(key, slice)` is the test. A list already knows how to slice itself: `self._words[key]` works for both ints and slices, so you only need to wrap the slice result in a new `Sentence`.

## Hint 3

```
__getitem__(self, key):
    if key is a slice: return type(self)(self._words[key])
    if key is an int:  return self._words[key]
    raise TypeError("indices must be integers or slices")
```
