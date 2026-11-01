## Hint 1

A thread's target cannot `return` a value to you: `Thread` ignores it. Where can a target
write its result so the main thread can read it afterwards? How would the target know **which
slot** is its own?

## Hint 2

Wrap `func` in a small inner function that knows its index:

```
results = [None] * len(args_list)
define call(index, args):
    results[index] = func(*args)
threads = [Thread(target=call, args=(i, args)) for each i, args]
for each t: t.start()        # loop 1: start all
for each t: t.join()         # loop 2: wait for all
return results
```

Why two loops and not `start(); join()` inside one loop?
