# The capture versus constant trap

A classmate wrote this and is confused:

```python
YES = "y"
NO = "n"
answer = input().strip().lower()
match answer:
    case YES:
        print("Saving")
    case NO:
        print("Not saving")
```

Python refuses to run it. After "fixing" it by deleting the `case NO:` branch and adding
`case _: print("Not saving")` at the end, it runs, but now prints `Saving` for every answer.

Write an explanation in `answer.md` that covers:

1. What a bare name like `YES` means inside a `case`, and what Python does with it.
2. Why the first version is a `SyntaxError`, and exactly what the error says it found.
3. Why the "fixed" version prints `Saving` for everything, and what happens to the variable
   `YES` afterwards.
4. The rule Python uses to tell a constant from a capture.
5. At least three correct ways to write this program.
6. Why Python was designed this way, instead of comparing with the variable's value.
