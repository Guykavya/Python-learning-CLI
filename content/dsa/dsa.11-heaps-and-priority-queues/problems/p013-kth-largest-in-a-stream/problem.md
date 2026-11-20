# K-th largest in a stream

Numbers arrive one at a time. After each new number you must say which number is the **k-th largest so far** (counting duplicates: in `[5, 5, 3]` the 1st largest is 5, the 2nd is 5, the 3rd is 3). Write the class

```python
class KthLargest:
    def __init__(self, k, nums): ...   # k >= 1; nums = the numbers seen so far (can be empty)
    def add(self, val): ...            # a new number arrives; return the k-th largest so far
```

Rules:

- `add(val)` returns the **k-th largest** of all the numbers seen so far (the ones in `nums` and all earlier `add` calls, plus `val`).
- While **fewer than `k` numbers** have been seen, the k-th largest does not exist: `add` returns **`None`**.
- `nums` can be shorter than `k`, empty, or much longer than `k`. The constructor must not change the list it receives.
- Keep only what you need: the class must use `O(k)` memory and `O(log k)` time per `add`. The tests count comparisons and the memory of 100,000 additions with `k = 5`.

## Example

```python
>>> s = KthLargest(3, [4, 5, 8, 2])
>>> [s.add(v) for v in (3, 5, 10, 9, 4)]
[4, 5, 5, 8, 8]

>>> t = KthLargest(3, [1])
>>> t.add(2)          # only two numbers seen so far
None
>>> t.add(3)          # 1, 2, 3 -> the 3rd largest is 1
1
```

Follow the first example: after `4, 5, 8, 2` the three largest are `4, 5, 8`, so the third largest is `4`. Adding `3` changes nothing (`3 < 4`). Adding `5` replaces `4`: now `5, 5, 8`, the answer is `5`.

## Constraints

- `1 <= k <= 10**4`. Up to `10**5` calls of `add`. Numbers fit in a normal `int` or `float`.

## Think about

Which numbers do you have to remember to answer "the k-th largest" at any moment? Which of them is the answer, and why can the others never become the answer again?
