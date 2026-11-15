# Trace the Lomuto partition

Predict **exactly** what this program prints. Do not run it.

```python
def partition(a, lo, hi):
    pivot = a[hi]
    i = lo
    for j in range(lo, hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
        print("j =", j, "i =", i, a)
    a[i], a[hi] = a[hi], a[i]
    return i


a = [7, 2, 9, 4, 3, 8, 5]
p = partition(a, 0, len(a) - 1)
print("pivot index", p, a)
b = [4, 4, 4, 4]
print(partition(b, 0, 3), b)
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

The pivot is the **last** element. `i` marks the first position of the "not smaller" zone; everything left of `i` is `< pivot`. For each `j`,
if `a[j] < pivot` swap it into position `i` and move `i` right. The line is printed after the possible swap. At the end the pivot is swapped into `a[i]`.
For the second call the print inside the loop still runs (3 lines) before the final `print` line.

## After you answer

1. After the call, what is true about every value left of the pivot index? And right of it?
2. What happens to the pivot index when all values equal the pivot (`b`)? What does that mean for quick sort on lists with many equal values?
3. Is Lomuto stable? Find a swap in the trace that moves a value past an equal one or past a larger one in an unstable way.
