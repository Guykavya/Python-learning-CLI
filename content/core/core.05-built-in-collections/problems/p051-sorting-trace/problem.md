# Sorting with keys

Predict **exactly** what this program prints, one line per printed line. Do not run it.
Draw names, lists and arrows on paper as you go.

```python
words = ["pear", "Fig", "kiwi", "apple", "date", "Banana"]
print(sorted(words))
print(sorted(words, key=str.lower))
print(sorted(words, key=len))
print(sorted(words, key=len, reverse=True))
print(sorted(words, key=len)[::-1])
nums = [3, -1, -3, 2, 1]
print(sorted(nums, key=abs))
print(max(nums, key=abs), min(nums, key=abs))
pairs = [(2, "b"), (1, "z"), (2, "a"), (1, "y")]
print(sorted(pairs))
d = {"x": 3, "y": 1, "z": 3}
print(sorted(d, key=d.get))
print(sorted(d, key=d.get, reverse=True))
result = nums.sort()
print(result, nums)
```

Write your answer in `answer.txt`.
