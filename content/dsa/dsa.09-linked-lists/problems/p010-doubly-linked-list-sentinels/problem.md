# Doubly linked list with sentinels

Build `DoublyLinkedList` with the node class `DNode` (given in `starter.py`: fields `val`, `prev`, `next`). Use **two sentinel nodes** (chapter section 5): `self.head` before the first item and `self.tail` after the last. They hold no data and are never removed; the list is empty when `self.head.next is self.tail`.

The method names follow `collections.deque`:

| Method | Does | Returns |
|---|---|---|
| `append(val)` | add at the right end | the new **node** |
| `appendleft(val)` | add at the left end | the new **node** |
| `pop()` | remove the rightmost item; `IndexError` if empty | its value |
| `popleft()` | remove the leftmost item; `IndexError` if empty | its value |
| `remove_node(node)` | unlink a node you hold (one returned by `append`/`appendleft`) | its value |
| `__len__()`, `__iter__()` | size; values from left to right | |

Every method is `O(1)`, including `remove_node`: holding the node is what makes that possible (a singly linked list would have to search for the node before it).

After every operation, the links must agree in both directions: for every node `x` between the sentinels, `x.next.prev is x` and `x.prev.next is x`. A removed node should have `prev` and `next` set to `None`, so it cannot keep other nodes alive or be used by mistake.

## Example

```python
>>> d = DoublyLinkedList()
>>> a = d.append(1); b = d.append(2); c = d.appendleft(0)
>>> list(d)
[0, 1, 2]
>>> d.remove_node(a)
1
>>> list(d), d.pop(), d.popleft(), len(d)
([0, 2], 2, 0, 0)
```

## Constraints

- The tests run 4,000 random operations against a `deque` model and check the links in both directions after each one.

## Think about

Write the four pointer assignments for inserting a node between `p` and `q`. In which order can you write them without losing anything? Why does the sentinel design need no `if` in `remove_node`?
