## Hint 1

Keep one list, `self._data`. Which of the three jobs moves an item **up** (one of them) and which moves an item **down** (two of them)? Write `_sift_up(i)` and `_sift_down(i)` as methods first; `push`, `pop` and the constructor then only call them.

## Hint 2

`pop` has three steps: remember the root, take the **last** item off the end of the list, and, if the list is not empty now, put that item into index 0 and sift it down. Do not use `list.pop(0)`: it shifts every item and breaks the shape. For an empty heap, raise `IndexError` before you touch the list.

The constructor needs the last parent: it is at index `len // 2 - 1`. Go from there **down to 0** and call `_sift_down` on each. Remember `list(items)` first, so the caller's list is not changed.

## Hint 3

```
class MinHeap:
    __init__(items=()):
        data = list(items)
        for i from len(data)//2 - 1 down to 0:
            sift_down(data, i)
    push(x):
        data.append(x);  sift_up(len(data) - 1)
    pop():
        if empty: raise IndexError
        top = data[0];  last = data.pop()
        if data:  data[0] = last;  sift_down(0)
        return top
    peek(): if empty raise IndexError; return data[0]
```
