# Explain: iterable versus iterator

Maya runs this in a Python shell:

```python
nums = [1, 2, 3]
it = iter(nums)
print(list(it))     # [1, 2, 3]
print(list(it))     # []
print(list(nums))   # [1, 2, 3]
print(list(nums))   # [1, 2, 3]
```

She is confused: "Why did the same call, `list(...)`, give `[]` the second time on `it`, but
works every time on `nums`?"

In `answer.md` (about 120 to 250 words), explain:

1. What is the difference between an **iterable** and an **iterator**? Use `nums` and `it` as examples.
2. Why can `it` be consumed only once, and why can `nums` be looped over again and again?
3. What does a `for` loop do with the object you give it, in terms of `iter()` and `next()`?
4. Give one practical consequence, for example what goes wrong if you loop over a generator twice.
