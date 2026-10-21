## Approach

`zip` pairs subjects with marks, `enumerate` numbers the rows, and `all` decides the overall
result.

## Code

```python
subjects = input().split()
marks = input().split()
if len(subjects) != len(marks):
    print("Mismatch")
else:
    print(f"{'No':<4}{'Subject':<12}{'Marks':>5}  Result")
    passed = 0
    for n, (subject, mark) in enumerate(zip(subjects, marks), start=1):
        ok = int(mark) >= 40
        passed += ok
        print(f"{n:<4}{subject:<12}{int(mark):>5}  {'PASS' if ok else 'FAIL'}")
    print(f"Passed {passed} of {len(subjects)}")
    overall = all(int(m) >= 40 for m in marks)
    print(f"Overall: {'PASS' if overall else 'FAIL'}")
```

## Why `passed += ok` works

`ok` is a `bool`, and `bool` is a kind of `int`: `True` adds 1 and `False` adds 0.

## Why "no subjects" gives PASS

`all()` of nothing is `True`: there is no failing subject. Whether that is the right school
rule is a separate question, but it is what `all` means.

## Another way

`overall = passed == len(subjects)` gives the same answer without a second pass.
