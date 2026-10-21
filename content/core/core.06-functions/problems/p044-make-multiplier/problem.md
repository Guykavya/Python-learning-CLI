# A multiplier factory

Write `make_multiplier(factor)` that returns a **new function**. The returned function takes
one number and returns it multiplied by `factor`.

**Examples**

```python
double = make_multiplier(2)
triple = make_multiplier(3)
double(10)          # 20
triple(10)          # 30
double(triple(5))   # 30
make_multiplier(0.5)(9)   # 4.5
```
