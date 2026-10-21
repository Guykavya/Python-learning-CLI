## Approach

For each number `x` at position `j`, the partner must be `target - x`. A dict from value to
its first position answers "have I seen the partner, and where?" in O(1). The first `j` that
finds a partner is the smallest `j`, and storing only first positions gives the smallest `i`.

## Code

```python
nums = [int(x) for x in input().split()]
target = int(input())
first_pos = {}
for j, x in enumerate(nums, start=1):
    need = target - x
    if need in first_pos:
        print(first_pos[need], j)
        break
    if x not in first_pos:
        first_pos[x] = j
else:
    print("No pair")
```

## Complexity

O(n) time and O(n) extra space. Trying all pairs is O(n²): about five billion pairs for
100,000 numbers.
