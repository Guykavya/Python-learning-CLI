# operator tools: pick columns, call methods, follow a path

The `operator` module gives you ready-made small functions, so you do not need a `lambda` for
every little job. Write three functions in `solution.py`.

### 1. `pick(rows, *indexes)`

Return a list with one **tuple** per row, holding the items at `indexes`. Use
`operator.itemgetter`.

Careful: `itemgetter(0, 2)` returns a tuple, but `itemgetter(0)` with **one** index returns the
item itself, not a tuple. Your `pick` must **always** give tuples. With no indexes at all,
raise `ValueError`.

```python
rows = [("ann", 31, "Pune"), ("bo", 25, "Delhi")]
pick(rows, 2, 0)    # [("Pune", "ann"), ("Delhi", "bo")]
pick(rows, 1)       # [(31,), (25,)]       one-item tuples, not [31, 25]
```

### 2. `call_method(items, name, *args)`

Return a list with `item.name(*args)` for every item. Use `operator.methodcaller`.

```python
call_method(["a,b", "c"], "split", ",")    # [["a", "b"], ["c"]]
call_method(["  hi ", "yo  "], "strip")    # ["hi", "yo"]
```

### 3. `get_path(data, *keys, default=None)`

Follow `keys` one by one into nested dicts and lists: `get_path(d, "a", "b", 1)` means
`d["a"]["b"][1]`. Use `functools.reduce` with `operator.getitem`.

If any step fails because a key is missing (`KeyError`), an index is out of range
(`IndexError`), or the value cannot be indexed (`TypeError`), return `default`.
With no keys, return `data` itself.

```python
config = {"db": {"hosts": ["a.local", "b.local"], "port": 5432}}
get_path(config, "db", "hosts", 1)          # "b.local"
get_path(config, "db", "user")              # None
get_path(config, "db", "port", 0, default="?")   # "?"   (an int cannot be indexed)
```
