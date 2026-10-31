## Hint 1

How many times must `timer()` be called for one batch? Where exactly do those calls go: inside
the inner loop that calls `fn`, or around it? What would happen to the result if you read the
clock around **every** call?

## Hint 2

Two nested loops: the outer one counts batches, the inner one calls `fn`. Keep a list of the
per-call times and take the `min` at the end.

```
check number >= 1 and repeat >= 1, else ValueError
per_call = []
repeat times:
    start = timer()
    number times: fn()
    end = timer()
    per_call.append((end - start) / number)
return min(per_call)
```
