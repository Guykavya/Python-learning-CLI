## Hint 1

What has to be true for `Stack[int]().pop()` to be known as an `int`? The class needs a placeholder for "the item type", and `push` and `pop` must use the *same* placeholder. How do you tell Python that a class has such a placeholder?

## Hint 2

Inherit from `Generic[T]`. Inside the class, write `T` in the hints of `push`, `pop` and `peek`. Keep the data in a plain list: what is the hint for an attribute that is "a list of T"? (`list[T]`, you may annotate it in `__init__`: `self._items: list[T] = []`.)

## Hint 3

```
class Stack(Generic[T]):
    __init__:      self._items = []   (hint: list[T])
    push(item):    append
    pop():         if empty: raise IndexError("pop from empty stack")
                   return last item removed
    peek():        if empty: raise IndexError(...)
                   return self._items[-1]
    is_empty():    return len == 0
    __len__():     return len(self._items)
```
