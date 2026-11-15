# Trace: partition around a value

`partition(head, x)` puts all nodes with values **smaller than** `x` before all the other nodes, keeping the original order inside each part (it is *stable*). It uses **two dummies** (chapter section 9, "Partition around a value"): nodes are appended to a "small" chain or a "big" chain, which are joined at the end. The helper `part` prints a chain from its dummy up to its current tail.

Predict **exactly** what this program prints. Do not run it.

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

def part(dummy, tail):
    """The values from dummy.next up to tail (tail included)."""
    out = []
    node = dummy
    while node is not tail:
        node = node.next
        out.append(str(node.val))
    return " -> ".join(out) if out else "empty"

def partition(head, x):
    small = small_tail = ListNode("S")
    big = big_tail = ListNode("B")
    cur = head
    while cur:
        if cur.val < x:
            small_tail.next = cur
            small_tail = cur
        else:
            big_tail.next = cur
            big_tail = cur
        print("took", cur.val, "| small:", part(small, small_tail), "| big:", part(big, big_tail))
        cur = cur.next
    big_tail.next = None
    small_tail.next = big.next
    return small.next

head = ListNode(3, ListNode(5, ListNode(8, ListNode(5, ListNode(10, ListNode(2, ListNode(1)))))))
print("result:", show(partition(head, 5)))
```

Write your answer in `answer.txt`, one printed line per line, for example `took 3 | small: 3 | big: empty`. The last line starts with `result:`.

## How to work

Keep two short lists on paper, "small" and "big". Walk the input `3, 5, 8, 5, 10, 2, 1` once. For each node decide its side (`val < 5`?), add it at the end of that side, and write the line. Equal to `x` counts as big.

## After you answer

1. Why does the code set `big_tail.next = None` before joining? Which node would otherwise still point where (look at the original list)?
2. Is the result sorted? What exactly does "stable" promise here?
3. What would the result be if every value were smaller than `x`? Which line makes that case work?
