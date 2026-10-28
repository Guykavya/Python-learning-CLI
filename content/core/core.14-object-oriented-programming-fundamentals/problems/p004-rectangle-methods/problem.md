# Rectangle methods that read and change self

Some methods only **read** the object and return an answer. Others **change** the object. Python's
own convention (think of `list.sort()` and `list.append()`): a method that changes the object in
place returns `None`, so nobody mistakes it for one that builds a new object.

Write a class `Rectangle` in `solution.py`:

- `Rectangle(width, height)` stores `width` and `height` as attributes.
- `r.area()` returns `width * height`.
- `r.perimeter()` returns `2 * (width + height)`.
- `r.is_square()` returns `True` if width and height are equal, else `False`.
- `r.scale(factor)` multiplies **both** width and height by `factor`, changing `r` **in place**, and
  returns `None`. If `factor` is zero or negative, raise `ValueError("factor must be positive")`
  and leave the rectangle unchanged.

**Example**

```python
r = Rectangle(3, 4)
print(r.area(), r.perimeter(), r.is_square())   # 12 14 False
result = r.scale(2)
print(result)                                   # None
print(r.width, r.height, r.area())              # 6 8 48
print(Rectangle(5, 5).is_square())              # True
```
