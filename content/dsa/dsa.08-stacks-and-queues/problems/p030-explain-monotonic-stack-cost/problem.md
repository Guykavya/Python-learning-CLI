# Explain: why is the monotonic stack `O(n)`?

Here is `next_greater` from the chapter (section 9):

```python
def next_greater(nums):
    ans = [-1] * len(nums)
    waiting = []
    for i, x in enumerate(nums):
        while waiting and nums[waiting[-1]] < x:
            ans[waiting.pop()] = x
        waiting.append(i)
    return ans
```

A classmate says: "There is a `while` inside a `for`. The `while` can run up to `n` times, and the `for` runs `n` times, so this is `O(n^2)`."

Write an explanation (8 to 12 sentences) in `answer.md`:

1. What exactly is wrong with the classmate's argument? Is it true that one `while` loop can run `n - 1` times? Give an input where that happens.
2. Prove that the **total** number of iterations of the `while` loop, over the whole run, is at most `n`. Count something that is easy to count.
3. Name this style of analysis, and give one more structure from this module where the same argument is used.
4. What is the total cost of the function, and the worst-case size of the stack? Give an input that reaches that size.

Then compare with the model answer and rate yourself.
