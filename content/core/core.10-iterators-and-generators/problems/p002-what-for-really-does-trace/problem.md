# What a for loop really does

This `while` loop is a hand-written version of a `for` loop. Predict everything it prints.

```python
items = ["a", "b", "c"]
it = iter(items)
while True:
    try:
        item = next(it)
    except StopIteration:
        print("done")
        break
    print("got", item)
print(next(it, "empty"))
print(list(it))
print(iter(it) is it)
print(type(it).__name__)
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`.
If you think the program stops with an error, the program catches it and prints a line, so you never need to write a traceback.
