# Explain: why lru_cache rejects a list

Ravi adds a cache to a slow function and gets an error he does not understand:

```python
from functools import lru_cache


@lru_cache(maxsize=None)
def total(prices):
    return sum(prices)


print(total((10, 20, 30)))    # 60
print(total([10, 20, 30]))    # TypeError: unhashable type: 'list'
```

Later he "fixes" a different function like this, and his reports start showing old numbers:

```python
stock = {"pen": 5}


@lru_cache(maxsize=None)
def stock_of(item):
    return stock[item]


print(stock_of("pen"))   # 5
stock["pen"] = 2
print(stock_of("pen"))   # 5   (still!)
```

In `answer.md` (about 150 to 300 words), explain:

1. How does `lru_cache` store results, and why does that need **hashable** arguments?
2. Why is it a **good** thing that Python refuses to use a list as a key? What could go wrong if
   a list were allowed and was changed after the call?
3. Give two ways to make `total` work with lists. Show short code for at least one.
4. What is wrong in the `stock_of` example? Which kind of function is safe to cache, and which is not?
