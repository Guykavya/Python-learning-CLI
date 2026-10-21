# Mutable versus immutable

Study these two short programs. The second uses a list, which you will study properly in core.05.
You only need to know that `append` adds an item to the end of a list.

```python
n = 5
m = n
n += 1
print(n, m)      # 6 5
```

```python
items = [5]
others = items
items.append(6)
print(items, others)   # [5, 6] [5, 6]
```

Explain in `answer.md`:

1. What "mutable" and "immutable" mean. Name at least four immutable types you know.
2. Why `m` did not change in the first program but `others` did change in the second.
3. What `n += 1` does to the object `n` referred to before, and what it does to the name `n`.
4. One advantage of immutable objects.
5. A rule of thumb to avoid surprises when two names share one object.
