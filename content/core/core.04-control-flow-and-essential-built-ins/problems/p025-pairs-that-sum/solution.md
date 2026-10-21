## Approach

Every unordered pair of positions, once. The inner loop starts at `i + 1`, so `j` is always
after `i`, and no position is paired with itself.

## Code

```python
nums = input().split()
target = int(input())
count = 0
for i in range(len(nums)):
    for j in range(i + 1, len(nums)):
        a = int(nums[i])
        b = int(nums[j])
        if a + b == target:
            print(f"{a} + {b}")
            count += 1
print(f"Pairs: {count}")
```

## Why `i + 1`

Starting `j` at 0 would see each pair twice (2 + 4 and 4 + 2) and pair positions with
themselves (3 + 3 from position 0 twice). Writing the dependency into the inner range is
cleaner than filtering it out with an `if`.

## Cost

For n numbers this checks n * (n - 1) / 2 pairs. Fine for hundreds of numbers; for millions,
a different method is needed (the DSA track covers it).

## Another way

`for i, a in enumerate(nums):` and `for b in nums[i + 1:]:` avoid the index arithmetic in the
inner loop.
