# Will the caller's data change?

For each function below, the caller runs:

```python
data = [3, 1, 2]
f(data)
print(data)
```

```python
def f1(lst):
    lst.sort()

def f2(lst):
    lst = sorted(lst)

def f3(lst):
    lst = lst[:]
    lst.append(99)

def f4(lst):
    lst += [4]

def f5(lst):
    lst = lst + [4]
    lst.sort()
```

In `answer.md`:

1. Say what `print(data)` shows after each of `f1` to `f5`.
2. For each, explain **why** in terms of objects and names: is the line mutating the object the
   caller passed, or rebinding the local name?
3. State the general rule in two or three sentences, and explain why "Python passes lists by
   reference and ints by value" is the wrong way to describe it.
