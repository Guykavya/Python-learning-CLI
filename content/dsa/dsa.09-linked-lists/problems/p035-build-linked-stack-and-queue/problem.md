# Build your own stack and queue on nodes

In dsa.08 you built stacks on Python lists and queues on `deque`. Now build both **from `ListNode`s only** (chapter section 11), with no Python list, `deque` or other container inside.

`LinkedStack`:

| Method | Does |
|---|---|
| `push(val)` | put `val` on top |
| `pop()` | remove and return the top value; `IndexError` if empty |
| `peek()` | return the top value without removing it; `IndexError` if empty |
| `__len__()` | number of items |

`LinkedQueue`:

| Method | Does |
|---|---|
| `enqueue(val)` | add `val` at the back |
| `dequeue()` | remove and return the front value; `IndexError` if empty |
| `peek()` | return the front value; `IndexError` if empty |
| `__len__()` | number of items |

Every operation must be **`O(1)`**: the stack works at the **head** of its chain; the queue removes at the head and adds at a **tail** pointer.

## Example

```python
>>> s = LinkedStack()
>>> s.push(1); s.push(2); s.push(3)
>>> s.pop(), s.peek(), len(s)
(3, 2, 2)
>>> q = LinkedQueue()
>>> q.enqueue(1); q.enqueue(2); q.enqueue(3)
>>> q.dequeue(), q.peek(), len(q)
(1, 2, 2)
```

## Constraints

- The tests compare both classes with a `deque` model over thousands of random operations, including emptying the queue completely and filling it again, and run 300,000 operations with a time limit.

## Think about

For the stack, why is the head the right end (what would `pop` at the tail of a singly linked list cost)? For the queue, which end adds and which removes, and why not the other way round? What must happen to the queue's tail when the last item is dequeued?
