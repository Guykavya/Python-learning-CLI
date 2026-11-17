# Trace heapify

This is the bottom-up `heapify` of chapter section 4, with prints. Predict **exactly** what it prints. Do not run it.

```python
def sift_down(a, i, n):
    swaps = 0
    while True:
        smallest = i
        l, r = 2 * i + 1, 2 * i + 2
        if l < n and a[l] < a[smallest]:
            smallest = l
        if r < n and a[r] < a[smallest]:
            smallest = r
        if smallest == i:
            return swaps
        print(f"swap a[{i}]={a[i]} with a[{smallest}]={a[smallest]}")
        a[i], a[smallest] = a[smallest], a[i]
        i = smallest
        swaps += 1

def heapify_traced(a):
    n = len(a)
    total = 0
    for i in range(n // 2 - 1, -1, -1):
        print(f"sift_down from index {i} (value {a[i]})")
        total += sift_down(a, i, n)
        print(f"-> {a}")
    print(f"total swaps: {total}")

data = [9, 4, 7, 1, 6, 2, 8]
heapify_traced(data)
print(data)
```

Write your answer in `answer.txt`, one printed line per line. Lists are printed the way Python prints them, for example `[9, 4, 2, 1, 6, 7, 8]`. Note that some lines have **no leading spaces**: type them exactly as the code builds them.

## How to work

Draw the tree of `[9, 4, 7, 1, 6, 2, 8]` (index `i` has the children `2i + 1` and `2i + 2`). Find the last parent: `n // 2 - 1`. Then handle one index at a time:

1. print the `sift_down from index ...` line with the value that sits at that index **now** (earlier sift-downs may have changed the list);
2. for every swap `sift_down` prints one `swap` line **before** it changes the list, with the values that are about to be swapped; the item that sinks is the first value in the line, and after the swap it has a new index, `smallest`;
3. after the whole `sift_down` call print the list.

## After you answer

1. How many `sift_down from index` lines are there, and which indexes were skipped? Why can they be skipped?
2. Index 0 needed two swaps. Which subtrees were already valid heaps at that moment, and what would break if the loop had started at index 0 instead of ending there?
3. Push the same seven numbers one by one into an empty heap (`push` = append, then sift up). Do you get the same list as `heapify`? Then try the numbers `7, 6, 5, 4, 3, 2, 1` with both methods. What does that say about "the" heap of a set of numbers?
