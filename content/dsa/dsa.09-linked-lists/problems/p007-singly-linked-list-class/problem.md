# Singly linked list class

Build a class `LinkedList` on top of `ListNode` (given in `starter.py`) that keeps three fields:

- `self.head`: the first node, or `None` when empty;
- `self.tail`: the last node, or `None` when empty;
- a size counter, so `len()` is `O(1)`.

Methods:

| Method | Does | Cost |
|---|---|---|
| `push_front(val)` | add `val` before the first item | `O(1)` |
| `push_back(val)` | add `val` after the last item | `O(1)` (use the tail) |
| `pop_front()` | remove and return the first value; `IndexError` if empty | `O(1)` |
| `remove(val)` | remove the **first** node holding `val`; return `True`, or `False` if not found | `O(n)` |
| `__len__()` | number of items | `O(1)` |
| `__iter__()` | yield the values from front to back (a generator) | |

The class must keep its **invariants** after every operation (chapter section 3):

1. empty: `head is None`, `tail is None`, length `0`;
2. not empty: `tail.next is None`, and walking from `head` ends at `tail`;
3. the size counter equals the number of nodes.

## Example

```python
>>> lst = LinkedList()
>>> lst.push_back(2); lst.push_back(3); lst.push_front(1)
>>> list(lst), len(lst)
([1, 2, 3], 3)
>>> lst.remove(3), lst.remove(9)
(True, False)
>>> lst.tail.val                # removing the last node moved the tail back
2
>>> lst.pop_front(), lst.pop_front(), len(lst)
(1, 2, 0)
>>> lst.head is None and lst.tail is None
True
```

## Constraints

- The tests run 3,000 random operations and compare with a Python list after each one, checking all three invariants.
- `push_back` must be `O(1)`: 200,000 pushes must finish within a few seconds.

## Think about

Which operations can make the list **empty**, and which can make it go from empty to one item? In those two moments both `head` and `tail` must change.
