# Total of any number of arguments

Write `total(*numbers)` that returns the sum of **any number** of numbers passed as separate
arguments. With no arguments the total is `0`.

Write the loop yourself; do not call the built-in `sum`.

**Examples**

```python
total(1, 2, 3)     # 6
total(10)          # 10
total()            # 0
total(1.5, -0.5)   # 1.0
values = [4, 5, 6]
total(*values)     # 15   (the star spreads the list into three arguments)
```
