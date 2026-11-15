# Trace: insert into a sorted list

`insert_sorted` keeps a list in ascending order, using a dummy node (chapter section 4). Here the dummy holds the text `"D"` so you can see when `prev` never moved. Predict **exactly** what this program prints. Do not run it.

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def show(node):
    parts = []
    while node is not None:
        parts.append(str(node.val))
        node = node.next
    return " -> ".join(parts) if parts else "None"

def insert_sorted(head, val):
    dummy = ListNode("D", head)
    prev = dummy
    while prev.next and prev.next.val < val:
        prev = prev.next
    prev.next = ListNode(val, prev.next)
    print("insert", val, "after", prev.val, ":", show(dummy.next))
    return dummy.next

head = None
for v in [4, 2, 6, 4, 1, 9]:
    head = insert_sorted(head, v)
```

Write your answer in `answer.txt`, one printed line per line, for example `insert 4 after D : 4` (the word `insert`, the value, `after`, the value of the node where `prev` stopped, a space, a colon, a space, then the list).

## How to work

For each call, start `prev` on the dummy `D` and move it forward **while the next node's value is smaller than the value being inserted**. The new node goes between `prev` and `prev.next`. Then write the whole list.

## After you answer

1. For which inserts did `prev` stay on the dummy? What do those inserts have in common?
2. The second `4` goes **before** or **after** the first `4`? Which single character in the code would change that?
3. Why does the empty list (the first call) need no special case?
