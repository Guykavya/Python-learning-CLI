# Counters with nonlocal

Write `make_counter(start=0, step=1)` that returns a function. Each call of that function
increases a private count by `step` and returns the new count.

Counters made by separate calls to `make_counter` must count independently. Use `nonlocal`.

**Examples**

```python
c = make_counter()
c(), c(), c()          # 1, 2, 3
d = make_counter(10, step=5)
d(), d()               # 15, 20
c()                    # 4
```
