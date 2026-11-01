## Hint 1

How can you test whether an object has a `__dict__` without crashing on a slotted one? What
single line in a class body removes the `__dict__`? For `compare_memory`, why does it matter that
all the instances are still alive while you measure, and what is the simplest way to keep them
alive?

## Hint 2

```
class Slotted:
    __slots__ = ("x", "y", "z")
    same __init__ as Plain

instance_size(obj):
    size = getsizeof(obj)
    if hasattr(obj, "__dict__"): size += getsizeof(obj.__dict__)
    return size

compare_memory(n):
    plains  = [Plain(i, i, i) for i in range(n)]
    slotted = [Slotted(i, i, i) for i in range(n)]
    return (sum of instance_size over plains, sum over slotted)
```
