# Trace building a max-heap

A **max-heap** stored in a list `a` has the parent of index `i` at `(i - 1) // 2`, children at `2i + 1` and `2i + 2`, and every parent is `>=` its children.
Predict **exactly** what this program prints. Do not run it.

```python
def sift_down(a, i, n):
    while True:
        left = 2 * i + 1
        right = 2 * i + 2
        largest = i
        if left < n and a[left] > a[largest]:
            largest = left
        if right < n and a[right] > a[largest]:
            largest = right
        if largest == i:
            break
        a[i], a[largest] = a[largest], a[i]
        print("swap index", i, "with", largest, a)
        i = largest


a = [3, 9, 2, 1, 4, 5]
n = len(a)
for start in range(n // 2 - 1, -1, -1):
    print("start", start)
    sift_down(a, start, n)
print(a)
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

Draw the tree for `[3, 9, 2, 1, 4, 5]`: index 0 has children 1 and 2, index 1 has children 3 and 4, index 2 has child 5. The loop starts at the last parent `n // 2 - 1 = 2`
and goes down to the root. Each `sift_down` swaps the value with its larger child until it is `>=` both children. A `start` line is printed for every start, even when no swap follows.

## After you answer

1. Why can the loop start at `n // 2 - 1` and skip the leaves?
2. When the root is sifted last, how many swaps did it need and why can it fall several levels?
3. How many swaps can `heapify` do at most? (Hint: the answer is `O(n)`, not `O(n log n)`.)
