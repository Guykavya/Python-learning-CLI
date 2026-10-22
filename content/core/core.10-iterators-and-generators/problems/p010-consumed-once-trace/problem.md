# What is left in the generator?

Predict the output. Watch which object is a generator and which is a list.

```python
squares = (n * n for n in range(4))
print(sum(squares))
print(sum(squares))
print(list(squares))
squares2 = [n * n for n in range(4)]
print(sum(squares2))
print(sum(squares2))
gen = (n for n in [1, 2])
print(bool(gen))
print(list(gen), bool(gen))
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`.
If you think the program stops with an error, the program catches it and prints a line, so you never need to write a traceback.
