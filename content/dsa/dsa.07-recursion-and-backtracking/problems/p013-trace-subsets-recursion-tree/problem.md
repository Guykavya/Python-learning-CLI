# Trace: the recursion tree of subsets

This is the "choose the next item from the rest" version of `subsets` (chapter section 6, view 2), with one extra `print` at the start of every call. It shows the `start` index and the current `path`.

Predict **exactly** what the program prints. Do not run it.

```python
def subsets(nums):
    result = []
    path = []

    def go(start):
        print(start, path)
        result.append(path[:])
        for i in range(start, len(nums)):
            path.append(nums[i])
            go(i + 1)
            path.pop()

    go(0)
    return result


answers = subsets([1, 2, 3])
print(len(answers))
```

Write your answer in `answer.txt`, one printed line per line, for example `2 [1, 2]` (the number, a space, then the list as Python prints it).

## How to work

Every call is one node of the recursion tree, and every node is a subset. The loop of a call tries the items at positions `start, start + 1, ...` in order; each choice makes a child node, whose `start` is one past the chosen position. Python runs the first child's whole sub-tree before the second child starts.

## After you answer

1. Which nodes are leaves (their loop does not run)? What is their `start`?
2. How many lines would `subsets([1, 2, 3, 4])` print before the final count?
3. Why does `[2, 1]` never appear?
