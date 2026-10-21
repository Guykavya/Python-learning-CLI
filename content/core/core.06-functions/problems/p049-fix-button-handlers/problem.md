# Repair the late-binding handlers

`starter.py` builds handler functions in loops, and every handler behaves like the last one.
Rewrite the two functions so each handler remembers its **own** value:

1. `make_handlers(names)` returns a dict mapping each name to a function of **no arguments**
   that returns `"Clicked <name>"`.
2. `make_adders(n)` returns a list of `n` functions; the function at index `i` takes one
   argument `x` and returns `x + i`.

The handlers must keep their exact signatures: `make_handlers` handlers take no arguments;
adders take exactly one.

**Examples**

```python
h = make_handlers(["Save", "Open"])
h["Save"]()     # 'Clicked Save'      (starter gives 'Clicked Open')
h["Open"]()     # 'Clicked Open'

adders = make_adders(3)
[add(10) for add in adders]   # [10, 11, 12]   (starter gives [12, 12, 12])
```
