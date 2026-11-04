## Approach

Split into two halves. The number of `(i, j)` with sum `s` is stored in a dictionary, and for each `(k, l)` every
`(i, j)` with sum `-(C[k] + D[l])` completes a valid quadruple. The count in the dictionary is exactly the number of
those pairs.

## Code

```python
n = int(input())
A = [int(x) for x in input().split()]
B = [int(x) for x in input().split()]
C = [int(x) for x in input().split()]
D = [int(x) for x in input().split()]

pair_count = {}
for a in A:
    for b in B:
        s = a + b
        pair_count[s] = pair_count.get(s, 0) + 1

answer = 0
for c in C:
    for d in D:
        answer += pair_count.get(-(c + d), 0)
print(answer)
```

## Complexity

O(n^2) time and O(n^2) memory (up to 250000 sums for `n = 500`). Compared with `n^4 = 6.25 * 10^10`.

## Another way

For `n = 500` you could also sort `C + D` sums and `A + B` sums and use two pointers: O(n^2 log n). The hash table
version is simpler. The trade-off is the memory for the dictionary.
