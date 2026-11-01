## Hint 1

A ctypes array *type* is made by multiplying a ctypes type by a number: `Point * 3`. How do you
then create an instance of that type from a list of pairs? What does `bytes(...)` of a ctypes
object give you? For the reverse direction, which class method of the array type builds an array
from bytes, and which one shares memory instead of copying? How many points fit in `len(data)`
bytes?

## Hint 2

```
class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int)]

make_points(pairs)   = (Point * len(pairs))(*pairs)       # each pair initialises one Point
sum_points(points)   = add p.x and p.y in a loop
pack_points(pairs)   = bytes(make_points(pairs))

count(nbytes): if nbytes % sizeof(Point): raise ValueError; return nbytes // sizeof(Point)
unpack_points(data)  = [(p.x, p.y) for p in (Point * count(len(data))).from_buffer_copy(data)]
view_points(buf)     = (Point * count(len(buf))).from_buffer(buf)
fits_c_int(v)        = ctypes.c_int(v).value == v
```
