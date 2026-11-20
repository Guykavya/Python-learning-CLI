# Meeting rooms I

Write `can_attend_all(meetings)`: can **one** person attend every meeting, never being in two at once?

Rules (chapter section 6):

- Each meeting is a pair `(start, end)` of integers with `start < end`, as a tuple or a list. The list is not sorted.
- Meetings are half-open `[start, end)`: **touching is fine**. A meeting that ends at 10 and one that starts at 10 can both be attended.
- Return `True` or `False`. No meetings (or one) can always be attended. Do not change the list you are given.

## Example

```python
>>> can_attend_all([(0, 30), (5, 10), (15, 20)])
False
>>> can_attend_all([(7, 10), (2, 4)])
True
>>> can_attend_all([(1, 5), (5, 8)])        # touching
True
```

## Constraints

- `0 <= len(meetings) <= 10**5`. Checking every pair is `O(n^2)`, far too slow; aim for `O(n log n)`.

## Think about

After sorting by start, why is it enough to compare each meeting only with the **next** one? Could meeting 1 clash with meeting 3 while meeting 2 fits between them?
