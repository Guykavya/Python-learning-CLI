# Explain: permutations with duplicates

Chapter section 8 removes duplicate permutations of `[1, 1, 2]` like this:

```python
def permutations_unique(nums):
    nums = sorted(nums)
    result, path = [], []
    used = [False] * len(nums)

    def go():
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            if i > 0 and nums[i] == nums[i - 1] and not used[i - 1]:
                continue
            used[i] = True
            path.append(nums[i])
            go()
            path.pop()
            used[i] = False

    go()
    return result
```

Answer in `answer.md`, in your own words (200 to 300 words):

1. Why does the plain `permutations` (no skip line) give 6 results for `[1, 1, 2]`, and how many of them are different?
2. Why must the list be **sorted** first?
3. Explain the condition `nums[i] == nums[i - 1] and not used[i - 1]`. Call the two 1s "1a" and "1b". Which of the orderings "1a before 1b" and "1b before 1a" does the rule keep, and why does that give each distinct permutation exactly once?
4. Why is this better than generating all `n!` orderings and putting them into a `set`? Give the numbers for `[1] * 10`.
