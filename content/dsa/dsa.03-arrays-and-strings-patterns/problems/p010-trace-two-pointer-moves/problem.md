# Trace two-pointer moves

This function searches a sorted list for two positions whose values add up to `target`. Each step prints
`i j sum move`. Predict **exactly** what the program prints. Do not run it.

```python
def pair(a, target):
    i, j = 0, len(a) - 1
    while i < j:
        s = a[i] + a[j]
        if s == target:
            print(i, j, s, "found")
            return (i, j)
        if s < target:
            print(i, j, s, "i+1")
            i += 1
        else:
            print(i, j, s, "j-1")
            j -= 1
    return None


print(pair([1, 3, 4, 6, 8, 11], 10))
print(pair([2, 5, 9, 14], 12))
```

Write your answer in `answer.txt`, one line per printed line. Step lines look like `0 5 12 j-1`.
Remember that the returned value is printed too.

## How to work

Write the list with the indices under it. Put a finger on `i` and one on `j`. For each step: add the two values,
compare with `target`, write the line, then move exactly one finger.

## After you answer

1. In the first call, which elements were thrown away, and why could none of them be part of the answer?
2. In the second call, how many steps ran before `i < j` failed? What is the most steps the loop can take for a list
   of length `n`?
