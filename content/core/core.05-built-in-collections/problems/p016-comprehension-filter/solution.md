## Approach

The three lines show the three shapes of comprehension:

- filter: `[n * n for n in nums if n % 2 == 0]`
- transform every item: `[n if n >= 0 else 0 for n in nums]`
- collect distinct values: `{n % 3 for n in nums}`

## Code

```python
nums = [int(x) for x in input().split()]
print([n * n for n in nums if n % 2 == 0])
print([n if n >= 0 else 0 for n in nums])
print(sorted({n % 3 for n in nums}))
```

## Complexity

Each line is O(n), plus O(k log k) to sort k distinct remainders (k is at most 3 here).

## Note

In Python, `-8 % 3` is `1`, not `-2`: the remainder takes the sign of the divisor (core.02).
