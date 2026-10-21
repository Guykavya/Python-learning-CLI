## Approach

A **sliding window**: consecutive blocks share all but two elements, so update instead of recomputing. The state to
keep is a dict `count` from code to the number of times it appears in the current block. Then the answer is
`len(count)`, provided codes whose count drops to 0 are deleted. Each step does O(1) dict work.

For `1 2 1 3 4 2 3`, `k = 3`: start `{1: 2, 2: 1}` (2). Add 3, remove 1: `{1: 1, 2: 1, 3: 1}` (3). Add 4, remove 2:
`{1: 1, 3: 1, 4: 1}` (3). And so on.

## Code

```python
n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

count = {}
for x in a[:k]:
    count[x] = count.get(x, 0) + 1
answers = [len(count)]

for i in range(k, n):
    entering = a[i]
    leaving = a[i - k]
    count[entering] = count.get(entering, 0) + 1
    count[leaving] -= 1
    if count[leaving] == 0:
        del count[leaving]
    answers.append(len(count))

print(" ".join(str(x) for x in answers))
```

## Complexity

O(n) time on average (the first block is O(k), then O(1) per step), O(k) space for the dict. The starter is O(n * k):
for `n = 10^5` and `k = 5 * 10^4` that is 2.5 * 10^9 element operations, against about 10^5 here.

## Another way

Instead of deleting keys, keep a separate variable `distinct` and change it when a count goes from 0 to 1 (`+1`) or from
1 to 0 (`-1`). Same complexity; a useful pattern when the dict must keep its keys.
