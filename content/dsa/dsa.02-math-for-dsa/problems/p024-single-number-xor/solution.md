## Approach

XOR has three properties: `x ^ x = 0`, `x ^ 0 = x`, and `a ^ b = b ^ a` with brackets free. So in the XOR of the whole list
every value that appears twice cancels itself, wherever its two copies are. What is left is the single value.

## Code

```python
n = int(input())
ans = 0
for x in input().split():
    ans ^= int(x)
print(ans)
```

## Complexity

O(n) time and O(1) extra space (apart from the input line itself).

## Another way

A dict or `Counter` of counts finds the value with count 1, O(n) time but O(n) extra space. Or keep a set: add on first
sight, remove on second sight; at the end the set holds one value. Sorting and comparing neighbours is O(n log n).
The XOR method is the one that needs no memory.
