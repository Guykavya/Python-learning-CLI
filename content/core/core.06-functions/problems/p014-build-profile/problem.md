# Build a profile from keyword arguments

Write `build_profile(name, **details)` that returns a **new** dict describing a person:

- the key `"name"` maps to `name`;
- every extra keyword argument becomes a key in the dict, **except** those whose value is
  `None` (treat `None` as "not given" and leave it out);
- keys appear in the order the keywords were passed, after `"name"`.

**Examples**

```python
build_profile("Asha", age=19, city="Pune")
# {'name': 'Asha', 'age': 19, 'city': 'Pune'}

build_profile("Ravi")
# {'name': 'Ravi'}

build_profile("Meena", email=None, phone="98111")
# {'name': 'Meena', 'phone': '98111'}

extra = {"city": "Delhi", "age": 21}
build_profile("Kiran", **extra)
# {'name': 'Kiran', 'city': 'Delhi', 'age': 21}
```

The caller's dict (`extra` above) must not change.
