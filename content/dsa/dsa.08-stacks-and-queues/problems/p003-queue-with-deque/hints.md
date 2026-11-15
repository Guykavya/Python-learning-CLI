## Hint 1

`from collections import deque`, then `self._items = deque()` in `__init__`. Which two deque methods give "add at the back" and "remove from the front", both in `O(1)`?

## Hint 2

```
enqueue: self._items.append(x)
dequeue: if empty -> raise IndexError("dequeue from empty queue")
         else return self._items.popleft()
front:   if empty -> raise IndexError("front of empty queue")
         else return self._items[0]
```
