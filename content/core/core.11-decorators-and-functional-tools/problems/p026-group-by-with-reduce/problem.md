# Group and count with reduce, without mutation

In functional style a step function never changes its input: it returns a **new** value. Write
three functions in `solution.py`, each using `functools.reduce`.

### 1. `group_by(items, key)`

Return a dict that maps `key(item)` to the list of items with that key, in their original order.
The keys appear in the order they are first seen.

```python
group_by(["apple", "bee", "avocado", "cat"], lambda w: w[0])
# {"a": ["apple", "avocado"], "b": ["bee"], "c": ["cat"]}
```

### 2. `count_by(items, key)`

Return a dict that maps `key(item)` to how many items have that key.

```python
count_by([3, 8, 5, 6, 1], lambda n: "even" if n % 2 == 0 else "odd")
# {"odd": 3, "even": 2}
```

### 3. `merge_counts(*counts)`

Each argument is a dict of counts. Return **one new dict** with the sums. Keys keep the order in
which they are first seen.

```python
merge_counts({"a": 2, "b": 1}, {"b": 5, "c": 1})    # {"a": 2, "b": 6, "c": 1}
merge_counts()                                     # {}
```

**Rules for all three**

- Do not change any argument. `merge_counts` must not change the dicts it receives.
- Every call starts fresh. Calling a function twice must give the same answer both times.
