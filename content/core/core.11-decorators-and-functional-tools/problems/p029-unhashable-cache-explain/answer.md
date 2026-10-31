**1. How the cache stores results.** `lru_cache` keeps a dict. The key is built from the
arguments of the call, and the value is the result. A dict finds a key by its **hash**, a number
computed from the key's value. So every argument must be hashable: numbers, strings, `None`, and
tuples of hashable items are; lists, dicts and sets are not. `total([10, 20, 30])` fails because
the list cannot be part of a dict key.

**2. Why refusing is good.** A list can change after it was used. If the list `[10, 20]` were a
key and then I did `prices.append(30)`, its hash would no longer match the place where the dict
stored it. The cache could return the old total for the new list, or never find the entry again.
Python prevents this whole class of silent bugs by only allowing values that cannot change.

**3. Making it work.** Convert at the call site: `total(tuple(prices))`. Or keep the cached
function private and add a small front door:

```python
@lru_cache(maxsize=None)
def _total(prices):
    return sum(prices)

def total(prices):
    return _total(tuple(prices))
```

**4. The `stock_of` bug.** The result depends on the global `stock`, not only on the argument.
The cache only looks at the argument, so after `stock` changes it still returns the old 5.
Caching is safe only for **pure** functions: same arguments, same result, and no side effects.
Do not cache functions that read changing global data, the clock, random numbers, files or the
network, or that print or write something, because a hit skips the body.
