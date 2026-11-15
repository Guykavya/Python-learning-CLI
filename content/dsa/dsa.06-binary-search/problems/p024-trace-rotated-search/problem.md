# Trace a search in a rotated array

Predict **exactly** what this program prints. Do not run it.

```python
a = [6, 7, 9, 15, 19, 2, 3, 4]
x = 3
lo, hi = 0, len(a) - 1
while lo <= hi:
    mid = (lo + hi) // 2
    if a[mid] == x:
        print("lo", lo, "mid", mid, "hi", hi, "found")
        break
    if a[lo] <= a[mid]:
        side = "left half sorted"
        if a[lo] <= x < a[mid]:
            hi = mid - 1
        else:
            lo = mid + 1
    else:
        side = "right half sorted"
        if a[mid] < x <= a[hi]:
            lo = mid + 1
        else:
            hi = mid - 1
    print("mid", mid, "a[mid]", a[mid], side, "-> lo", lo, "hi", hi)
else:
    print("not found")
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

The array is `[6, 7, 9, 15, 19, 2, 3, 4]` and we look for 3. In each step decide first which half is sorted (`a[lo] <= a[mid]` means the left half is), then whether the target fits inside it.
The program prints one line per step, and a different line at the moment it finds the target. Python prints the word after `mid` literally.

## After you answer

1. In step 1 the left half `[6, 7, 9, 15]` is sorted. Why is 3 not inside it, and which side do we take?
2. In step 2 which half is sorted? What are its bounds?
3. How many probes were needed? Compare with a plain linear scan of 8 elements.
