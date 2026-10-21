# Dict views are live

Predict **exactly** what this program prints, one line per printed line. Do not run it.
Draw names, lists and arrows on paper as you go.

```python
d = {"a": 1, "b": 2}
k = d.keys()
v = d.values()
it = d.items()
snap = list(d.items())
d["c"] = 3
print(list(k))
print(sum(v))
print(len(it), len(snap))
del d["a"]
print(list(k), "a" in k)
d["a"] = 10
print(list(d))
print(("a", 10) in it)
e = d | {"b": 0, "z": 26}
print(e)
d |= {"b": 20}
print(list(v))
print(k == {"b", "c", "a"})
```

Write your answer in `answer.txt`.
