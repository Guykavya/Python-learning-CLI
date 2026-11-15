# Trace insertion sort

Predict **exactly** what this program prints. Do not run it.

```python
a = [4, 3, 2, 10, 12, 1]
shifts = 0
for i in range(1, len(a)):
    key = a[i]
    j = i - 1
    while j >= 0 and a[j] > key:
        a[j + 1] = a[j]
        shifts += 1
        j -= 1
    a[j + 1] = key
    print("i =", i, "key =", key, a, "shifts so far", shifts)
print(a)
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

Keep the sorted prefix `a[0..i-1]` in mind. Each round takes `key = a[i]`, moves every larger value one place to the right (a **shift**, not a swap),
and drops `key` into the gap. The print happens after the key is placed. While shifting, the list temporarily has the key's value twice: ignore that, only the printed state matters.

## After you answer

1. Which rounds needed zero shifts? What does that say about inputs that are almost sorted?
2. The total shifts equal the number of inversions in the start list. Count them to check yourself.
3. Why is `a[j] > key` (strict) important for stability?
