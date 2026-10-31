## Hint 1

`copy.copy(x)` calls `x.__copy__()` if it exists; `copy.deepcopy(x, memo)` calls
`x.__deepcopy__(memo)`. Inside them you must create a new object **without** running
`__init__` (which would need arguments). How? `type(self).__new__(type(self))` gives an empty
instance of the right class.

## Hint 2

For `__copy__`: copy all attributes at once with `new.__dict__.update(self.__dict__)`, then
replace the ones that need their own value (`lines`, `tags`, `_cache`).
For `__deepcopy__`: loop over `self.__dict__.items()`. Which key is shared, which is reset, and
the rest go through `copy.deepcopy(value, memo)`. Why must you pass `memo` along?

## Hint 3

A cycle (A -> B -> A) works only if the new A is registered in `memo` **before** its attributes
are copied, so that when the copy reaches A again it finds the new A.

```
__deepcopy__(self, memo):
    new = type(self).__new__(type(self))
    memo[id(self)] = new               # first!
    for key, value in self.__dict__.items():
        owner  -> new.owner = value
        _cache -> new._cache = {}
        other  -> setattr(new, key, copy.deepcopy(value, memo))
    return new
```
