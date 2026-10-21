# Why UnboundLocalError?

This program works:

```python
visits = 0

def show():
    print("visits:", visits)

show()
```

After adding one line, it crashes:

```python
visits = 0

def record():
    print("visits:", visits)
    visits = visits + 1

record()
```

```text
UnboundLocalError: cannot access local variable 'visits' where it is not associated with a value
```

In `answer.md`, explain:

1. Why the first version can read the global `visits`.
2. Why the second version fails on the `print` line, which comes **before** the new line.
   Mention when Python decides that a name is local.
3. How you can see that decision for yourself (hint: the function's `__code__`).
4. Two different fixes, and which you would prefer in real code and why.
5. Whether `visits_list.append(1)` inside a function (with a global list `visits_list`) would
   cause the same error, and why.
