## Approach

Two pointers start at the head; per round `slow` takes one step and `fast` two. After `r` rounds `slow` is on index `r` and `fast` on index `2r`. The loop stops when `fast` is on the last node (odd length) or past it (`None`, even length). For `n = 5`: two rounds, `slow` on index 2. For `n = 6`: three rounds, `slow` on index 3, the second middle.

## Code

```python
def middle_node(head):
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next             # one step
        fast = fast.next.next        # two steps
    return slow
```

## Complexity

`O(n)` time (`fast` crosses the list once), `O(1)` extra memory.

## Another way

Count the nodes in one walk, then walk `n // 2` steps from the head. It is also `O(n)` and `O(1)` memory, with two walks instead of one. The fast/slow version matters because the same two pointers find the middle for merge sort (problem 25) and the palindrome check (problem 27), and detect cycles (problem 17), where counting is impossible.
