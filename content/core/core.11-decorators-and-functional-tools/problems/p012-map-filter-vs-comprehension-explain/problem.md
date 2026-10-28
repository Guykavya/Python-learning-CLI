# Explain: map and filter versus a comprehension

Three ways to get the squares of the even numbers:

```python
nums = [1, 2, 3, 4, 5, 6]

a = list(map(lambda n: n * n, filter(lambda n: n % 2 == 0, nums)))
b = [n * n for n in nums if n % 2 == 0]

squares = map(lambda n: n * n, nums)
print(list(squares))   # [1, 4, 9, 16, 25, 36]
print(list(squares))   # []

words = ["  ann ", "bo "]
c = list(map(str.strip, words))   # ['ann', 'bo']
```

In `answer.md` (about 120 to 250 words), explain:

1. Why `a` and `b` give the same list, and say in words what `map` and `filter` each do.
2. Why the second `print(list(squares))` gives `[]`. What kind of object does `map` return? (Connect it to
   what you learnt about iterators.)
3. When does `map` read **better** than a comprehension (look at `c`), and when does a comprehension read
   better? Give one rule of thumb.
