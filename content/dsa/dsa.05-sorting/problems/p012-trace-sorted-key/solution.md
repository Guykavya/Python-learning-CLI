## Approach

Compute the key of each element, then order by key; ties keep input order in every call, including with `reverse=True`.

## Expected output

```text
['fig', 'pear', 'kiwi', 'date', 'plum', 'apple']
['apple', 'pear', 'kiwi', 'date', 'plum', 'fig']
['plum', 'pear', 'kiwi', 'fig', 'date', 'apple']
['fig', 'date', 'kiwi', 'pear', 'plum', 'apple']
['apple', 'date', 'kiwi', 'pear', 'plum', 'fig']
['apple', 'date', 'fig', 'kiwi', 'plum', 'pear']
['pear', 'fig', 'apple', 'kiwi', 'date', 'plum']
[-1, 2, 3, -4]
None
[-4, -1, 2, 3]
```

## Why

`reverse=True` is implemented so that the result is the same as sorting descending while keeping equal elements in their original order. That is why line 2 is not line 1 backwards. The tuple key lets you order ties yourself. `list.sort()` returns `None` by design so that nobody mistakes it for a copy.
