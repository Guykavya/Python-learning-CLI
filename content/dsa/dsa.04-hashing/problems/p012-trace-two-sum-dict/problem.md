# Trace the complement lookup

This function looks for two numbers that add up to `target`. For each number `x` it asks the dictionary
"have I already seen `target - x`?" Predict **exactly** what the program prints. Do not run it.

```python
def find(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        need = target - x
        print("i =", i, "x =", x, "need =", need, "seen =", seen)
        if need in seen:
            print("pair", seen[need], i)
            break
        seen[x] = i
    else:
        print("no pair")


find([4, 9, 1, 6, 5, 3, 2], 8)
find([3, 3], 6)
find([5], 10)
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

Keep a table of `seen` (value -> index). On each step compute `need = target - x`, print the line with the **current**
`seen`, then test and store. Remember that `seen` is printed as a dictionary: `{4: 0, 9: 1}`.

## After you answer

1. Why does the second call (`[3, 3]`) still find a pair although `seen` holds only one `3`?
2. Why must the store `seen[x] = i` come **after** the check?
3. What would the function do for `[5]` with target 10?
