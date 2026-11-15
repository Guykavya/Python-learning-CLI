# Trace: next greater element

This is the chapter's monotonic stack (section 9, "The idea: a waiting room") with prints added. `waiting` holds **indices** of numbers that have not found their next greater element yet. Predict **exactly** what the program prints. Do not run it.

```python
nums = [2, 1, 2, 4, 3]
ans = [-1] * len(nums)
waiting = []
for i, x in enumerate(nums):
    while waiting and nums[waiting[-1]] < x:
        j = waiting.pop()
        ans[j] = x
        print("pop", j)
    waiting.append(i)
    print(i, x, waiting, ans)
print(ans)
```

Write your answer in `answer.txt`, one printed line per line, exactly as Python prints it. The `pop` lines look like `pop 1`; the other lines look like `2 2 [0, 2] [-1, 2, -1, -1, -1]` (index, value, the `waiting` list of **indices**, the `ans` list).

## How to work

For each `i`, first do all the pops (each one prints a line), then the push, then the line for `i`. The `while` compares the **value** of the index on top (`nums[waiting[-1]]`) with `x`, and pops only while it is **strictly** smaller.

## After you answer

1. At `i = 2`, why does index 0 stay in `waiting`?
2. Read the values of `waiting` (not the indices) after each step. Are they ever increasing from bottom to top?
3. How many pushes and how many pops happen in total? Why can there never be more pops than pushes?
