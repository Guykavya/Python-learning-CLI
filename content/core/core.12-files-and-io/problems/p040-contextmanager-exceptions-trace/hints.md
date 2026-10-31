## Hint 1

Take `work()` first. Which `section` is entered first, and what happens at the line `{}["x"]`?
Which of the two sections has `swallow=KeyError`?

## Hint 2

```
a enters -> got A -> b enters -> got B -> KeyError at {}["x"]
   -> thrown into b at its yield -> b's except KeyError matches -> prints "swallowed KeyError"
   -> finally prints "exit b" -> the with of b ends normally, so the code goes on with "after b"
return "done" -> a's finally runs "exit a" -> only then does print(work()) get the value
```

For section `c`: `swallow=KeyError` but the error is `ValueError`. Is it caught inside `section`?
