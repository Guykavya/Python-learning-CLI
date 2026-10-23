# Iterable or iterator: who runs out?

Predict the output. Think about which object remembers a position.

```python
nums = [10, 20, 30]
it = iter(nums)
print(next(it))
print(list(it))
print(list(it))
print(list(nums))
print(list(nums))
print(iter(nums) is iter(nums))
print(iter(it) is it)
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`.
If you think the program stops with an error, the program catches it and prints a line, so you never need to write a traceback.
