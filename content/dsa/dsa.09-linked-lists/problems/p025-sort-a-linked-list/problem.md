# Sort a linked list

Write `sort_list(head)` that sorts the chain in non-decreasing order and returns the new head, using **merge sort** (chapter section 8):

1. split the list in two halves (fast and slow pointers find the middle; cut the link between the halves);
2. sort each half recursively;
3. merge the two sorted halves (problem 23).

Rules:

- Rewire the nodes: no new nodes (except dummies inside the merge), no copying values into a Python list, no swapping values between nodes. Every node keeps its own `val`.
- **Stable**: nodes with equal values keep their original order.
- `O(n log n)` time. The tests sort 50,000 nodes with a time limit.

## Example

```python
>>> to_list(sort_list(from_list([4, 2, 1, 3])))
[1, 2, 3, 4]
>>> to_list(sort_list(from_list([-1, 5, 3, 4, 0])))
[-1, 0, 3, 4, 5]
>>> sort_list(None) is None
True
```

## Constraints

- `0 <= n <= 5 * 10**4`. The recursion depth is only about `log2 n` (17 for 100,000), so recursion is fine here.

## Think about

For a list of **two** nodes, which split do `slow = head, fast = head` and `slow = head, fast = head.next` give? One of them never makes the list smaller. Why is merge sort a better fit for linked lists than quicksort or heapsort?
