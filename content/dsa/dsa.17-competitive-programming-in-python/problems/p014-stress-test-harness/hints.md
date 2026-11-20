## Hint 1

Where does the loop start, and what makes the sequence of cases repeatable? Think about *when* the `random.Random(seed)` object is created.

## Hint 2

If `fast` sorts its argument in place and you then give the same list to `brute`, `brute` sees a different input. Which module function makes an independent copy of nested data?

## Hint 3

```text
rng = random.Random(seed)
repeat trials times:
    case = gen(rng)
    a = call(fast, copy.deepcopy(case))
    b = call(brute, copy.deepcopy(case))
    if differ(a, b): return case, a, b
return None
```
where `call` returns the result, or the exception object if it raised; `differ` treats two exceptions of the same type as equal.
