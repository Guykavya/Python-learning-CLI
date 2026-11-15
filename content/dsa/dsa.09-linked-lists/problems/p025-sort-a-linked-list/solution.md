## Approach

Merge sort fits linked lists perfectly: splitting needs no random access (fast and slow pointers), and merging needs no extra array (only relinking). Sort each half recursively and merge them with the stable `merge_two` of problem 23. Starting `fast` one node ahead makes `slow` stop at the end of the first half; for two nodes that gives halves of one node each, so the recursion always shrinks.

## Code

```python
def merge_two(a, b):
    dummy = ListNode()
    tail = dummy
    while a is not None and b is not None:
        if b.val < a.val:                    # ties: a first, so the sort is stable
            tail.next = b
            b = b.next
        else:
            tail.next = a
            a = a.next
        tail = tail.next
    tail.next = a if a is not None else b
    return dummy.next


def sort_list(head):
    if head is None or head.next is None:
        return head
    slow, fast = head, head.next             # slow stops at the end of the first half
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
    second = slow.next
    slow.next = None                         # cut the list in two
    return merge_two(sort_list(head), sort_list(second))
```

## Complexity

`O(n log n)` time: `log2 n` levels, and on each level the splits and merges touch every node a constant number of times. Extra memory: `O(log n)` for the recursion stack; no array of size `n`.

## Another way

**Bottom-up merge sort** needs no recursion: merge runs of length 1 into runs of 2, then runs of 2 into runs of 4, and so on, walking the list each round with a dummy and a tail. It uses `O(1)` extra memory but the code is longer (a `split(head, size)` helper that cuts off `size` nodes and returns the rest). In real Python code you would copy the values into a list and call `sorted()`, which is faster because it runs in C; the point here is to practise the pointer version.
