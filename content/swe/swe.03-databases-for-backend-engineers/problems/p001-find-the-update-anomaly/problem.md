# Find the update anomaly

A flat table repeats facts on every row. When one copy changes and another does not, the table **contradicts itself** (chapter section 3.2). Write

```python
conflicting_facts(rows, key, field)
```

`rows` is a list of dicts (rows of a flat table). For every distinct value of `row[key]`, collect the distinct values of `row[field]` in the order they first appear. Return a dict with only the keys that have **more than one** value:

```python
rows = [
    {"order": 1, "customer": "c1", "email": "a@x.com"},
    {"order": 2, "customer": "c1", "email": "a@x.com"},
    {"order": 3, "customer": "c2", "email": "b@x.com"},
    {"order": 4, "customer": "c2", "email": "bee@x.com"},
]
conflicting_facts(rows, "customer", "email")      # {"c2": ["b@x.com", "bee@x.com"]}
```

An empty list gives `{}`. A key with one value (even if it appears on many rows) is not a conflict.
