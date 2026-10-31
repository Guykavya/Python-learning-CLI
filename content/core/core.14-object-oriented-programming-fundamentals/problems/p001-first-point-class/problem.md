# Your first class: a Point

A point on a flat map has two numbers, `x` and `y`. Instead of passing two loose numbers to every
function, you bundle them into one object with a class.

Write a class `Point` in `solution.py`:

- `Point(x, y)` stores the two numbers in the attributes `x` and `y`.
- `p.distance_to(other)` returns the straight-line distance from `p` to the point `other`, as a
  float. The formula is `sqrt((x2 - x1)**2 + (y2 - y1)**2)`.
- `p.moved(dx, dy)` returns a **new** `Point` that is `dx` to the right and `dy` up from `p`.
  It must **not** change `p` itself.

**Example**

```python
a = Point(0, 0)
b = Point(3, 4)
print(b.x, b.y)            # 3 4
print(a.distance_to(b))    # 5.0
c = a.moved(2, -1)
print(c.x, c.y)            # 2 -1
print(a.x, a.y)            # 0 0   (a did not change)
print(c is a)              # False (moved gave a new object)
```
