## Approach

A palindrome means "first half equals reversed second half". A singly linked list cannot walk backwards, so make the second half walk backwards for a moment: reverse it in place, compare, and reverse it back. The first half still ends at `slow`, whose `next` points at the old start of the second half (now its last node), so after the comparison `slow.next = reverse_list(second)` reconnects everything exactly as before.

For odd lengths, `slow` stops on the middle node, which stays in the first half; the second half is one node shorter, and the loop stops when it runs out, so the middle is never compared (it equals itself anyway).

## Why it works

The comparison is correct because node `i` of the reversed second half is node `n - 1 - i` of the original list, so the loop checks `values[i] == values[n - 1 - i]` for every `i` in the first half. **Why restore?** `is_palindrome` is a question, and asking a question must not change the answer to the next one. Without step 4 the caller's list would end in the middle (`slow.next` still points at the old second-half start, whose `next` is now `None`), so half the data would silently disappear for everyone who holds the head. Changing shared data temporarily is acceptable only if every path, including the early "not a palindrome" answer, puts it back.

## Code

```python
def reverse_list(head):
    prev = None
    while head is not None:
        nxt = head.next
        head.next = prev
        prev = head
        head = nxt
    return prev


def is_palindrome(head):
    if head is None or head.next is None:
        return True
    slow, fast = head, head.next             # slow stops at the end of the first half
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
    second = reverse_list(slow.next)         # reverse the second half
    a, b = head, second
    result = True
    while b is not None:                     # the second half is not longer than the first
        if a.val != b.val:
            result = False
            break
        a = a.next
        b = b.next
    slow.next = reverse_list(second)         # restore the list
    return result
```

## Complexity

`O(n)` time (find the middle, reverse, compare, reverse back: four passes over at most `n` nodes). `O(1)` extra memory.

## Another way

Copy the values into a list and compare it with its reverse: `vals == vals[::-1]`. That is the right answer in everyday code: `O(n)` time and `O(n)` memory, one line, and the list is never touched. A recursive version with a pointer from the front also exists, but it uses `O(n)` stack frames.
