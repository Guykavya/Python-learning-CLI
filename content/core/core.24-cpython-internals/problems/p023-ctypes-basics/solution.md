## Approach

`ctypes.Structure` with `_fields_` describes the C layout. Multiplying the struct type by `n` gives
a C array type: one contiguous block of `n * 8` bytes, with no per-item Python objects (an
element becomes a Python-visible `Point` only when you index it). `bytes(obj)` copies a ctypes
object's raw memory; `from_buffer_copy` goes the other way; `from_buffer` makes the array use the
buffer's memory directly. Checking the length first turns a confusing ctypes error into a clear
`ValueError`.

## Code

```python
import ctypes


class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int)]


def make_points(pairs):
    array_type = Point * len(pairs)
    return array_type(*pairs)


def sum_points(points):
    total_x = total_y = 0
    for p in points:
        total_x += p.x
        total_y += p.y
    return (total_x, total_y)


def pack_points(pairs):
    return bytes(make_points(pairs))


def _count(nbytes):
    size = ctypes.sizeof(Point)
    if nbytes % size:
        raise ValueError(f"{nbytes} bytes is not a whole number of {size}-byte points")
    return nbytes // size


def unpack_points(data):
    array = (Point * _count(len(data))).from_buffer_copy(data)
    return [(p.x, p.y) for p in array]


def view_points(buf):
    return (Point * _count(len(buf))).from_buffer(buf)


def fits_c_int(value):
    return ctypes.c_int(value).value == value
```

Memory comparison (Python 3.14, 64-bit, your numbers may differ): a list of 1,000 `(x, y)` tuples
of small ints costs about 9 KB for the list plus 1,000 tuples of 64 bytes each, roughly 73 KB in
total (the small ints themselves are shared and not counted). The ctypes array is 8,000 bytes. That compactness, and the fixed layout, is why C libraries
and binary file formats work with arrays like these.

## Complexity

O(n) for building, packing, unpacking and summing n points. `view_points` is O(1): it copies
nothing.

## Another way

The `struct` module packs the same bytes without defining a type:

```python
import struct

def pack_points(pairs):
    flat = [v for pair in pairs for v in pair]
    return struct.pack(f"{len(flat)}i", *flat)

def unpack_points(data):
    if len(data) % 8:
        raise ValueError("not a whole number of points")
    values = struct.unpack(f"{len(data) // 4}i", data)
    return list(zip(values[0::2], values[1::2]))
```

`struct` is the simpler tool for files and network messages. `ctypes` adds named fields, arrays
you can modify in place, shared memory with `from_buffer`, and (in real projects) calling C
functions in shared libraries, which this exercise deliberately leaves out.
