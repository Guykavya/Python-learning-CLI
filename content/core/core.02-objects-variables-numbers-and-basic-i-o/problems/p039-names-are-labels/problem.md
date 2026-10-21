# Assignment is not copying

Look at this program and its output:

```python
a = 10
b = a
print(a is b)   # True
a = a + 1
print(a, b)     # 11 10
print(a is b)   # False
```

Explain in your own words, in `answer.md`:

1. What a name (variable) is in Python, and what `b = a` actually does.
2. Why `print(a is b)` is `True` on line 3.
3. Why `b` is still `10` after `a = a + 1`, and why `a is b` is now `False`.
4. What `id()` would show at each step.
5. Why the "variable is a box that holds a value" picture is misleading in Python, and a better picture.

Use small examples and simple diagrams made of text if they help.
