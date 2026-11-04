# Trace three-sum pointers with duplicate skips

The three-sum search sorts the array, fixes `a[i]`, and runs a two-pointer search on the part to its right. To avoid
printing the same triplet twice it **skips duplicates** in three places. This version prints every comparison and
every skip. Predict **exactly** what the program prints. Do not run it.

```python
def three_sum(a):
    a.sort()
    print("sorted", *a)
    found = []
    n = len(a)
    for i in range(n - 2):
        if i > 0 and a[i] == a[i - 1]:
            print("skip i", i)
            continue
        l, r = i + 1, n - 1
        while l < r:
            s = a[i] + a[l] + a[r]
            if s < 0:
                print(i, l, r, s, "l+1")
                l += 1
            elif s > 0:
                print(i, l, r, s, "r-1")
                r -= 1
            else:
                print(i, l, r, s, "found")
                found.append((a[i], a[l], a[r]))
                l += 1
                r -= 1
                while l < r and a[l] == a[l - 1]:
                    print("skip l", l)
                    l += 1
                while l < r and a[r] == a[r + 1]:
                    print("skip r", r)
                    r -= 1
    return found


print(three_sum([-1, 0, 1, 2, -1, -4]))
print(three_sum([0, 0, 0, 0]))
print(three_sum([3, 1, -4, 2, 3, 1]))
```

Write your answer in `answer.txt`, one line per printed line. Comparison lines look like `0 1 5 -3 l+1`
(`i l r sum move`), skip lines look like `skip l 2`, and the result lines look exactly as Python prints a list of
tuples.

## How to work

First write the sorted array with its **indices** under it. For each `i`, start a small table with the columns
`l`, `r`, `sum`, `move`. Three things are easy to miss:

- After `found`, **both** pointers move first, and only then do the two skip loops run.
- Each skip loop checks `l < r` **before** comparing values. When the pointers meet, a skip loop prints nothing.
- The `range(n - 2)` loop and the `continue` for a repeated `a[i]`: which values of `i` print `skip i`?

## After you answer

1. In the first call, why does `i = 0` (value -4) find nothing? What is the largest sum it can make?
2. In the second call, `l` and `r` meet right after `found`. Why does no `skip l` line appear even though
   `a[2] == a[1]`?
3. Remove the line `if i > 0 and a[i] == a[i - 1]: ... continue` in your head. Which triplet would the first
   call report twice?
4. Why does the method need the array sorted? Name two places in the code that rely on it.
