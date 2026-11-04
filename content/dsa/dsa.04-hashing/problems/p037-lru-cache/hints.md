## Hint 1

Which key is evicted: the one used longest ago. How could a dictionary keep the keys sorted by recency of use?

## Hint 2

On every use, `value = cache.pop(k)` then `cache[k] = value`: the key now sits at the end. The oldest key is the first one in the dictionary.

## Hint 3

```
get: if k in cache: v = cache.pop(k); cache[k] = v; print v  else print -1
put: if k in cache: del cache[k]
     elif len(cache) == c: del cache[next(iter(cache))]
     cache[k] = v
```
