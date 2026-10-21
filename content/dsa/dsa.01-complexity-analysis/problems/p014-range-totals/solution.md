## Approach

Precompute once, answer fast. A **prefix sum** list `before` stores the total of the first `k` days for every `k`.
Building it is one pass. Then any range total is a difference of two stored values, because the first `l - 1`
days appear in both `before[r]` and `before[l - 1]` and cancel.

For `3 -1 4 1 5`: `before = [0, 3, 2, 6, 7, 12]`. Days 2 to 5: `before[5] - before[1] = 12 - 3 = 9`.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]
q = int(input())

before = [0] * (n + 1)
for k in range(n):
    before[k + 1] = before[k] + a[k]

for k in range(q):
    l, r = [int(x) for x in input().split()]
    print(before[r] - before[l - 1])
```

## Complexity

- Time: O(n + q). O(n) to build, O(1) per question. The starter is O(n * q).
- Space: O(n) for `before`.

## Another way

`itertools.accumulate(a)` builds the running totals for you (add `[0]` in front). The idea, paying once up front so
that many later questions become cheap, is called precomputation. Prefix sums are the most important example;
dsa.03 develops them further (2D prefix sums, difference arrays).
