# The loop that only looks quadratic

`a` is sorted. The first part of this program counts the pairs of positions `i < j` whose values differ by less than
`k`, using a `while` loop inside a `for` loop. The second part does a similar job but resets `j` every time.
`inner` and `inner2` count how many times each `while` body runs.

Predict **exactly** what it prints. Do not run it.

```python
a = [1, 2, 4, 7, 8, 11, 15, 16]
k = 4
n = len(a)

j = 0
inner = 0
pairs = 0
for i in range(n):
    while j < n and a[j] - a[i] < k:
        j += 1
        inner += 1
    pairs += j - i - 1
print("inner", inner)
print("pairs", pairs)

inner2 = 0
for i in range(n):
    j = i
    while j < n and a[j] - a[i] < k:
        j += 1
        inner2 += 1
print("inner with reset", inner2)
```

Write your answer in `answer.txt`, one line per printed line.

## After you answer

1. In the first part, can `inner` ever be bigger than `n`, whatever the list and `k` are? Why?
2. What is the Big-O of each part for a general sorted list of length `n`? Give an input that makes the second part
   as slow as possible.
