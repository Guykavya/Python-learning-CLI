# Palindrome list in O(1) space

Write `is_palindrome(head)` that returns `True` if the values read the same forwards and backwards.

The easy way copies the values into a Python list (`O(n)` memory). Here you must use **`O(1)` extra memory** (the tests measure it):

1. find the middle with fast and slow pointers;
2. **reverse the second half** in place (problem 12);
3. compare the first half with the reversed second half, node by node;
4. **reverse the second half back**, so the list is exactly as it was (same nodes, same order). The caller still owns the list; a check must not leave it broken.

## Example

```python
>>> is_palindrome(from_list([1, 2, 2, 1])), is_palindrome(from_list([1, 2, 3, 2, 1]))
(True, True)
>>> is_palindrome(from_list([1, 2])), is_palindrome(None)
(False, True)
```

## Constraints

- `0 <= n <= 10**5`.

## Think about

For odd lengths, where does the middle node go: first half, second half, or neither? Does comparing it matter? Why must the list be restored even when the answer is `False` (no early `return` before step 4)?
