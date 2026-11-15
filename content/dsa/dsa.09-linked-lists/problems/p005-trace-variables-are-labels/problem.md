# Trace: variables are labels

Six names, four nodes, a few rewirings. Predict **exactly** what this program prints. Do not run it.

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

a = ListNode(1, ListNode(2, ListNode(3)))
b = a.next
c = b.next
d = ListNode(4)
e = a
d.next = b
a.next = c
b.val = 20
f = e.next
e = d
c = c.next

print("a:", show(a))
print("b:", show(b))
print("c:", show(c))
print("d:", show(d))
print("e:", show(e))
print("f:", show(f))
print(a.next is f, e is d, d.next is b)
```

Write your answer in `answer.txt`, one printed line per line, exactly as Python prints it. The first six lines look like `a: 1 -> 3` (the name, a colon, a space, then the values from that node to the end joined by ` -> `, or `None`). The last line is three `True`/`False` words separated by spaces.

## How to work

Draw the four nodes as boxes `[1]`, `[2]`, `[3]`, `[4]` and every name as a sticky note with an arrow to **one box** (or to `None`). Go line by line:

- `x = y` moves the sticky note `x` to the box that `y` points at. No box changes.
- `x.next = y` changes the **arrow inside** box `x`. No sticky note moves.
- `x.val = ...` changes the number written in a box. Every name pointing at that box sees it.

Only print at the end, by following the arrows from each name's box.

## After you answer

1. Which line changed what `b` prints, without `b` itself being reassigned?
2. After `e = d`, does node `1` still exist? Which name keeps it alive?
3. Why does `c = c.next` not change the list `a` prints?
