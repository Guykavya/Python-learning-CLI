# A read-only proxy that counts reads

You want to hand an object to some code (a plugin, a report template) so it can **read**
everything but **change** nothing, and you want to know which attributes it actually used.
Wrapping the object in a proxy does both, and `__getattr__` makes the wrapper tiny: it is
called only for names the proxy itself does not have, so everything else is forwarded.

Copy `starter.py` to `solution.py` and write `ReadOnlyProxy(target)`:

1. **Reads are delegated.** `proxy.price` returns `target.price`. It is a live view, not a
   copy: if the target changes later, the proxy shows the new value. Methods work too, and
   they run on the real target (`proxy.total()` is `target.total()`).
2. **Writes and deletes are refused.** `proxy.price = 5` and `del proxy.price` raise
   `AttributeError` whose message contains the attribute name (for example
   `cannot set 'price': read-only proxy`). The target is not changed.
3. **Reads are counted per name.** `proxy.access_count("price")` returns how many times
   `price` was read successfully through the proxy (0 if never). Reading a missing attribute
   raises the target's `AttributeError` and is not counted.
4. `repr(proxy)` is `ReadOnlyProxy(<repr of target>)`.
5. **No recursion traps.** `copy.copy(proxy)` must work and give a proxy for the same target.

Two traps hide in this small class:

- Your own `__setattr__` blocks **every** assignment, including the ones in `__init__`. Use
  `object.__setattr__(self, name, value)` there.
- `copy.copy` creates the new object **without calling `__init__`**, then asks it
  `hasattr(new, "__setstate__")`. If your `__getattr__` reads `self._target` and `_target` does
  not exist yet, Python calls `__getattr__("_target")`, which reads `self._target`, which calls
  `__getattr__("_target")`... until `RecursionError`. Inside `__getattr__`, fetch your own
  attributes in a way that cannot call `__getattr__` again (for example
  `object.__getattribute__(self, "_target")`, or `vars(self)`), and let a missing one end as
  an `AttributeError`.

Special methods are looked up on the **type**, not through `__getattr__`, so `len(proxy)` does
not reach the target's `__len__`. That is fine here; only plain attribute reads are required.

**Example**

```python
class Order:
    def __init__(self, items):
        self.items = items
        self.paid = False

    def total(self):
        return sum(self.items)

order = Order([10, 5])
view = ReadOnlyProxy(order)
view.items                    # [10, 5]
view.total()                  # 15
view.paid = True              # AttributeError: cannot set 'paid': read-only proxy
order.paid = True
view.paid                     # True (live view)
view.access_count("paid")     # 1
view.access_count("total")    # 1
view                          # ReadOnlyProxy(<__main__.Order object at 0x...>)  (address differs)
```
