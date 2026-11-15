# Trace: the three-variable reversal

This is the iterative reversal of the chapter (section 6), with a print after each step. Predict **exactly** what it prints. Do not run it.

```python
class ListNode:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next

def show(node):
    parts = []
    while node is not None:
        parts.append(str(node.val))
        node = node.next
    return " -> ".join(parts) if parts else "None"

def name(node):
    return "None" if node is None else node.val

head = ListNode(1, ListNode(2, ListNode(3, ListNode(4))))
prev = None
cur = head
step = 0
while cur:
    nxt = cur.next
    cur.next = prev
    prev = cur
    cur = nxt
    step += 1
    print(f"step {step}: prev={name(prev)} cur={name(cur)} nxt={name(nxt)} | reversed: {show(prev)}")
print("head is now", name(prev), "and old head 1 points to", name(head.next))
```

Write your answer in `answer.txt`, one printed line per line, for example `step 1: prev=1 cur=2 nxt=2 | reversed: 1` (the values of the three variables, or `None`, then the reversed part as values joined by ` -> `). The last line starts with `head is now`.

## How to work

Make a table with the columns `step`, `nxt`, the arrow that was flipped, `prev`, `cur`. Fill it one row per loop pass, in the order of the four lines in the loop. Draw the arrows after each row: the reversed part grows from the **left** of the old list, and `prev` is always its first node.

## After you answer

1. After the loop, why do `cur` and `nxt` print the same thing on every line?
2. Which node does `head` point to at the end, and why is that node now the **last** one?
3. What would happen if the loop body started with `cur.next = prev` and only then saved `nxt = cur.next`?
