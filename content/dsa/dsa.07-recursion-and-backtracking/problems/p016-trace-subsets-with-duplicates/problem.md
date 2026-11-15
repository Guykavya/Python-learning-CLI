# Trace: subsets with duplicates

When the input contains equal values, the plain `subsets` produces the same subset twice. The fix (chapter section 6): sort, then **skip a value that equals the previous one at the same level of the loop** (`i > start`). This program prints every node it visits and every branch the skip rule cuts.

Predict **exactly** what it prints. Do not run it.

```python
def subsets_unique(nums):
    nums = sorted(nums)
    result, path = [], []

    def go(start):
        print("visit", path)
        result.append(path[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                print("skip i =", i, "start =", start)
                continue
            path.append(nums[i])
            go(i + 1)
            path.pop()

    go(0)
    return result


print(len(subsets_unique([2, 1, 2])))
```

Write your answer in `answer.txt`, one printed line per line, for example `visit [1, 2]` or `skip i = 2 start = 1`.

## How to work

First sort the input: `nums` becomes `[1, 2, 2]` (positions 0, 1, 2). Draw the tree of calls: for each node, write its `start` and loop over `i = start .. 2`. At every `i` ask: is `i > start` **and** `nums[i] == nums[i - 1]`? If yes, a `skip` line is printed and no child is created.

## After you answer

1. Why is `[1, 2, 2]` still produced, although the second 2 equals the first one?
2. Which subset would be produced twice without the skip rule?
3. What would change with `i > 0` instead of `i > start`? (Chapter section 6 shows the answer.)
