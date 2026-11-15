# Trace: the order of swap-based permutations

The swap method (chapter section 8) puts each item at position `i` by swapping it there, recurses, and swaps back. It produces the permutations in a different order than the `used`-list method. This program prints all 24 permutations of `[1, 2, 3, 4]`, six per line.

Predict **exactly** what it prints. Do not run it.

```python
def permutations_swap(nums):
    nums = list(nums)
    result = []

    def go(i):
        if i == len(nums):
            result.append(nums[:])
            return
        for j in range(i, len(nums)):
            nums[i], nums[j] = nums[j], nums[i]
            go(i + 1)
            nums[i], nums[j] = nums[j], nums[i]

    go(0)
    return result


perms = permutations_swap([1, 2, 3, 4])
for start in range(0, 24, 6):
    print(" ".join("".join(str(x) for x in p) for p in perms[start:start + 6]))
```

Write your answer in `answer.txt`: four lines, each with six 4-digit words separated by single spaces, for example `1234 1243 ...`.

## How to work

The swap at level 0 decides the first digit; everything below it is the same algorithm on the last three positions. Two facts help:
- the swaps are undone after each call, so at the start of each loop iteration the list is exactly as it was when the call began;
- for 3 items `[a, b, c]` the order is `abc acb bac bca cba cab` (shown in the chapter for `[1, 2, 3]`).

## After you answer

1. Why is the 5th permutation `1432` and not `1423`?
2. Is the output in sorted (lexicographic) order? Which method gives sorted order?
