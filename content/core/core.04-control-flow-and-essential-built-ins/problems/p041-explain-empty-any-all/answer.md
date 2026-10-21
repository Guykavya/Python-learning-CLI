**What they do.** `any(items)` and `all(items)` are short loops:

```python
# any(items)
result = False
for item in items:
    if item:
        result = True
        break

# all(items)
result = True
for item in items:
    if not item:
        result = False
        break
```

`any` searches for a truthy item. `all` searches for a falsy item, a **counter-example**.

**The empty case.** With no items, neither loop body runs, so each keeps its starting value:
`any` gives `False` (no truthy item was found) and `all` gives `True` (no counter-example was
found). That is not a special rule; it falls straight out of the meaning. Everyday version:
"every student in this empty classroom is wearing red" is true, because you cannot point to a
student who is not. Logicians call this *vacuous truth*. It also keeps the rules consistent:
`all(a + b)` should equal `all(a) and all(b)`, which only works if `all([])` is `True`.

**Short-circuiting.** Both stop at the first item that settles the answer:

```python
text = "a1"
print(any(ch.isdigit() for ch in text))   # stops at "1"
print(all(ch.isdigit() for ch in text))   # stops at "a"
```

With a generator expression, items after that point are never even computed, which matters
when computing them is slow or could crash.

**A real bug.** A "digits only" check:

```python
text = input()
if all(ch.isdigit() for ch in text):
    number = int(text)       # crashes on an empty line!
```

If the user just presses Enter, `text` is `""`, `all` says `True`, and `int("")` raises
`ValueError`. Fix it by requiring at least one character: `if text and all(...)`. (The
string method `text.isdigit()` already returns `False` for `""` for exactly this reason.)

**Fit with sum and max.** `sum([])` is `0`: the neutral value for adding, just as `True` is
the neutral value for `and` and `False` for `or`. `max([])` has no neutral value (there is
no "smallest possible thing" for every type), so it raises `ValueError` unless you supply
`default=`.

Key ideas to check: loops with starting values; vacuous truth; short-circuit; empty-input
bug and the `text and` guard; neutral values and `default=`.
