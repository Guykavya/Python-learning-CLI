## Hint 1

Stack: the newest item must be the easiest to reach, so keep it at the head. `push` creates a node that points at the old top. Which single line does `pop` need to make the next node the top?

## Hint 2

Queue: removing at the head is `O(1)`; adding at the head too, but then you would remove the newest item. So add at the **tail**, which you keep in `self._tail`. Two border cases: enqueue on an empty queue sets both `_head` and `_tail`; dequeue of the last item must set `_tail` to `None` as well.

## Hint 3

```
push(val):    top = ListNode(val, top); size += 1
pop():        if top is None: raise IndexError; node = top; top = node.next; size -= 1; return node.val
enqueue(val): node = ListNode(val)
              if tail is None: head = tail = node
              else: tail.next = node; tail = node
dequeue():    if head is None: raise IndexError
              node = head; head = node.next
              if head is None: tail = None
```
