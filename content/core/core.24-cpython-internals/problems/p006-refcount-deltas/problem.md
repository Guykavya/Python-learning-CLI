# Measure extra references

Every CPython object carries a **reference count**: how many references (names, list slots,
dict entries, attributes...) point at it. When it drops to zero the object is freed at once.
`sys.getrefcount(obj)` reports that count, but the absolute number is not useful:

- the call itself holds a temporary reference, and different versions count that differently
  (3.14 can *borrow* a local variable's reference instead of adding one);
- since 3.12, objects like `None`, `True`, small ints and many strings are **immortal**: their
  count is a huge fixed number that never changes.

What *is* reliable is a **difference** measured on a brand-new, ordinary object: count, do one
thing, count again.

Copy `starter.py` to `solution.py` and write **`extra_refs(store)`**:

1. create a brand-new object with `object()` inside the function (never a number or string, they
   may be immortal or shared);
2. read its reference count;
3. call `store(obj)`, which stores the object somewhere and **returns** the container it used;
   keep that returned value in a variable so the container stays alive;
4. read the count again and return `after - before`.

**Example**

```python
extra_refs(lambda o: [o])            # 1   one list slot
extra_refs(lambda o: [o, o, o])      # 3   three slots, same object
extra_refs(lambda o: {"key": o})     # 1   a dict value
extra_refs(lambda o: (o, {o: 1}))    # 2   a tuple slot and a dict key
extra_refs(lambda o: None)           # 0   nothing kept
```

Use `sys.getrefcount` exactly the same way for both readings, so whatever the version does with
temporary references cancels out.
