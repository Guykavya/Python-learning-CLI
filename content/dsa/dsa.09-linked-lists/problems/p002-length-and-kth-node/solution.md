## Approach

Both functions walk with a variable `cur` that starts at `head` and moves `cur = cur.next`.

- `length` counts one per node until `cur` is `None`.
- `get` takes `k` steps. If the chain ends before that (`cur is None` before a step), index `k` does not exist. If the chain has exactly `k` nodes, the last step lands on `None`, which is also the right answer.

## Code

```python
def length(head):
    count = 0
    cur = head
    while cur is not None:
        count += 1
        cur = cur.next
    return count


def get(head, k):
    if k < 0:
        return None
    cur = head
    for _ in range(k):
        if cur is None:          # the list ended before index k
            return None
        cur = cur.next
    return cur
```

## Complexity

`length` is `O(n)`; `get` is `O(k)` (at most `O(n)`). Both use `O(1)` extra memory. Compare a Python list: `len(a)` and `a[k]` are `O(1)`, because a list stores its size and its items in one numbered block. This is the price of a chain.

## Another way

`get` can be written as a `while` loop that counts down: `while cur is not None and k > 0: cur = cur.next; k -= 1`, then `return cur`. Same steps, one condition. Classes like `LinkedList` in problem 7 keep a `size` field, so their length is `O(1)`.
