# Where does a generator pause?

Predict the exact output, including the order of the lines printed by the generator and by the main program.

```python
def steps():
    print("start")
    yield 1
    print("middle")
    yield 2
    print("end")


g = steps()
print("created")
print(next(g))
print("between")
print(next(g))
try:
    next(g)
except StopIteration:
    print("stop")
print(list(g))
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`.
If you think the program stops with an error, the program catches it and prints a line, so you never need to write a traceback.
