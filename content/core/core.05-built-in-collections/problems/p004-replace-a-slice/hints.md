## Hint 1

Read the numbers with a comprehension: `[int(x) for x in input().split()]`. The same works for the
replacement line, and an empty line gives an empty list.

## Hint 2

`i, j = [int(x) for x in input().split()]` unpacks the two positions.

## Hint 3

`nums[i:j] = new` does all the work. Print with `" ".join(str(n) for n in nums)`.
