## Hint 1

For each first position `i`, which second positions `j` should you try so that every pair is
seen exactly once?

## Hint 2

`j` starts just after `i`: `range(i + 1, len(nums))`.

## Hint 3

```
for i in range(len(nums)):
    for j in range(i + 1, len(nums)):
        if int(nums[i]) + int(nums[j]) == target: print and count
```
