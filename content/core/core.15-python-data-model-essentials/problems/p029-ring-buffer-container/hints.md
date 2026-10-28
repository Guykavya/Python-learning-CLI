## Hint 1

A ring buffer is a plain list of fixed size plus a number that says where the oldest item is. When the buffer is full, where does the next item go? What changes after you overwrite the oldest slot?

## Hint 2

Keep three things: a list `[None] * capacity`, `_start` (index of the oldest item) and `_size`. The item at logical position `i` (0 = oldest) lives in physical slot `(_start + i) % capacity`. Use that one formula in `__getitem__` and `__iter__`.

## Hint 3

```
append(x):
    if size < capacity: slot = (start + size) % capacity ; store ; size += 1
    else:               store at slot `start` ; start = (start + 1) % capacity
__getitem__(i):  TypeError if not int; if i < 0: i += size; IndexError unless 0 <= i < size
                 return items[(start + i) % capacity]
__iter__:        for i in range(size): yield items[(start + i) % capacity]
```
