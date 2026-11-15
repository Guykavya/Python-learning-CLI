## Approach

Schoolbook addition, column by column, starting at the ones digit, which is conveniently the head. A column adds the carry and the digits that exist (a list that has ended contributes 0). `divmod(total, 10)` gives the new carry and the digit for the result. The result is built with a dummy and a tail. The loop condition includes the carry, so `99 + 1` gets its last digit `1`.

## Code

```python
def add_two_numbers(a, b):
    dummy = ListNode()
    tail = dummy
    carry = 0
    while a is not None or b is not None or carry:
        total = carry
        if a is not None:
            total += a.val
            a = a.next
        if b is not None:
            total += b.val
            b = b.next
        carry, digit = divmod(total, 10)
        tail.next = ListNode(digit)
        tail = tail.next
    return dummy.next
```

## Complexity

`O(max(n, m))` time, one pass over both lists; the result has at most `max(n, m) + 1` nodes. `O(1)` extra memory besides the result.

## Another way

If the digits were stored **most significant first** (`3 -> 4 -> 2`), you would reverse both lists (problem 12), add as here, and reverse the result; or push the digits onto two stacks (dsa.08) and pop them, building the result by pushing at the front. Python could also do `int(...)` conversion trivially because its integers have no size limit, but in languages with 64-bit integers that fails for long numbers, which is why the problem exists.
