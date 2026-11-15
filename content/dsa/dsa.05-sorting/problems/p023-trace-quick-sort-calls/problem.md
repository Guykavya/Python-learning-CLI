# Trace the quick sort recursion

Predict **exactly** what this program prints. Do not run it.

```python
def quick(a, lo, hi, depth):
    if lo >= hi:
        print("depth", depth, "base", lo, hi)
        return
    pivot = a[hi]
    i = lo
    for j in range(lo, hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]
    print("depth", depth, "pivot", pivot, "at", i, a)
    quick(a, lo, i - 1, depth + 1)
    quick(a, i + 1, hi, depth + 1)


a = [6, 3, 8, 1, 5]
quick(a, 0, len(a) - 1, 0)
print(a)
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

This is the Lomuto partition from problem p013 with the **last element** as pivot. Each call prints one line, either `base` (range of size 0 or 1) or `pivot ... at ... a`, **after**
the partition, and then recurses on the left part first and on the right part second (depth-first). Track `lo`, `hi` for every call on paper.

## After you answer

1. Draw the call tree. What is its depth for this input?
2. What happens to the depth if the input is already sorted? Try `[1, 2, 3, 4, 5]` on paper.
3. Which pivot rule would avoid that?
