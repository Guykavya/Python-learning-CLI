# Trace dictionary basics

Predict **exactly** what this program prints. Do not run it.

```python
ages = {}
ages["ana"] = 30
ages["ben"] = 25
ages["ana"] = 31
print(ages)
print(len(ages))
print(ages.get("cy"))
print(ages.get("cy", 0))
print("ben" in ages, "Ben" in ages)
del ages["ben"]
ages["dev"] = 40
for name in ages:
    print(name, ages[name])
print(list(ages.items()))
print(ages.pop("ana"), ages)
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

Draw a table with a row per key. Updating an existing key changes its value but **not** its position. Deleting a key
and adding it back later puts it at the end. Remember that `print` of a dictionary uses braces, `'key': value`, and
`print` of a list of pairs uses `[('key', value), ...]`.

## After you answer

1. Why did `ages["ana"] = 31` not create a second `ana`?
2. Is `"Ben" in ages` true? Why does it matter that string keys are case sensitive?
3. What does `.get` do that `ages["cy"]` would not?
