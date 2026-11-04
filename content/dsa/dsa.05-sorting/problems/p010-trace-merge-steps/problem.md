# Trace the merge step

Predict **exactly** what this program prints. Do not run it.

```python
def merge(left, right):
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
        print("out =", out, "i =", i, "j =", j)
    out.extend(left[i:])
    out.extend(right[j:])
    return out


print(merge([1, 4, 7], [2, 4, 9, 10]))
print(merge([], [3]))
print(merge([5, 6], [1, 2]))
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

For each call write a small table with columns `i`, `j`, `left[i]`, `right[j]`, which one is taken. The `print` inside the loop runs after each
taken value. The two `extend` calls run once after the loop and print nothing. Note `<=`: on a tie the value from `left` goes first.

## After you answer

1. In the first call, which `4` came first in the output, the one from `left` or from `right`? How can you tell from the `i` and `j` values?
2. Which call never enters the loop? Which call ends with all of `right` taken before any of `left`?
3. How many comparisons does a merge of lists of sizes `n` and `m` make at most?
