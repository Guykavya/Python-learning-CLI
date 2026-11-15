## Approach

Start with the widest pair. The sorted order tells us which end to drop: a sum that is too small can only grow by
moving `i` right, a sum that is too big can only shrink by moving `j` left. Every step removes one candidate, so at
most `n - 1` steps run.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]
target = int(input())

i, j = 0, n - 1
answer = "-1"
while i < j:
    s = a[i] + a[j]
    if s == target:
        answer = f"{i + 1} {j + 1}"
        break
    if s < target:
        i += 1
    else:
        j -= 1

print(answer)
```

## Complexity

O(n) time, O(1) extra memory. The checks for all pairs would be O(n^2): about 2 * 10^10 for `n = 200000`.

## Another way

For each value remember its **last** position in a dict. Then go through `i` from the left and look up
`target - a[i]`; the first `i` whose partner sits at a position after `i` gives the same pair. This works on
unsorted arrays too, costs O(n) memory, and is the idea behind the "two sum" problem.
