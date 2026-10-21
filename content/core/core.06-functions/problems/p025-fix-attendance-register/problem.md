# Fix the attendance register

A classmate wrote three small functions for a class attendance register. Each function looks
fine when you call it once, but the program behaves strangely in real use. `starter.py`
contains their code. **Find and fix the bugs** so every function matches its description:

1. `mark_present(name, register=None)` adds `name` to `register` unless it is already there,
   and returns the register. If no register is passed, it starts a **new** one for this call.
   If the caller passes a register, that list is filled in place.
2. `absent_students(all_students, register)` returns a **new** list of the students in
   `all_students` who are not in `register`, in the order of `all_students`. Neither argument
   may change.
3. `sorted_register(register)` returns a **new** list of the names sorted alphabetically,
   ignoring case. The register itself must keep its original order.

**Example of the strange behaviour**

```python
mark_present("Asha")        # ['Asha']
mark_present("Ravi")        # ['Asha', 'Ravi']   <- should be ['Ravi']

everyone = ["Asha", "Ravi", "Meena"]
absent_students(everyone, ["Ravi"])   # ['Asha', 'Meena']  correct...
everyone                               # ['Asha', 'Meena']  <- Ravi vanished from the class!
```

Change as little as possible: the intended logic is right; the way it treats its arguments is not.
