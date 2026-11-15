# Build and print a list

`starter.py` gives you the node class from the chapter (section 2):

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
```

Write the two helpers that every other problem of this module uses:

1. `from_list(values)` builds a chain of new `ListNode`s holding the items of the Python list `values`, in order, and returns the **head** (the first node). An empty list gives `None`: an empty linked list is simply "no first node".
2. `to_list(head)` walks the chain from `head` and returns a Python list of the values. `to_list(None)` is `[]`. It must not change the chain.

## Example

```python
>>> head = from_list([1, 2, 3])
>>> head.val, head.next.val, head.next.next.val
(1, 2, 3)
>>> head.next.next.next is None
True
>>> to_list(head)
[1, 2, 3]
>>> from_list([]) is None
True
>>> to_list(None)
[]
```

## Constraints

- `0 <= len(values) <= 10**5`, so use loops, not recursion.
- Values can be anything (numbers, strings, `None`, ...). Do not stop the walk when a **value** is falsy: stop when the **node** is `None`.

## Think about

After `from_list([1, 2, 3])`, which variables still point to node `1`? Why does `from_list` need a second variable (a `tail`) besides the head?
