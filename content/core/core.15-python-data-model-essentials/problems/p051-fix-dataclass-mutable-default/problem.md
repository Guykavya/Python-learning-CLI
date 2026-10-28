# Fix: three shared defaults

This is the **fix** assessment of the module. Ravi wrote three small classes for a shop script.
Each one has a bug about **a default value that is shared when it should be new each time**.

```python
cart_a, cart_b = Cart("asha"), Cart("ravi")
cart_a.add("pen")
cart_b.items            # ['pen']        <- Ravi's cart contains Asha's pen!

Tags()                  # TypeError: 'set' object is not callable

c1, c2 = Counter(), Counter()
c1.hit("x")
c2.counts               # {'x': 1}       <- c2 never counted anything
```

**Find and fix the three bugs.** Copy the starter into `solution.py` and fix it. Rules:

- Every class must be a **dataclass** (`Cart` is a plain class today: convert it).
- Each object gets its **own** `items` list, `names` set or `counts` dict. A list or dict that
  is passed in explicitly is stored as it is.
- The methods `add`, `count` and `hit` keep their behaviour. `Tags.add` stores names in lower case.
- Remove the module-level `SHARED_COUNTS`: nothing may write into it any more.

Reminder: dataclass refuses `items: list = []` with a `ValueError`; the way to say "a new empty list
for each object" is `field(default_factory=list)`.

**Example** (after the fix)

```python
a, b = Cart("asha"), Cart("ravi")
a.add("pen")
b.items              # []
Cart("asha")         # Cart(owner='asha', items=[])
Tags().names         # set()
Counter().counts     # {}
```
