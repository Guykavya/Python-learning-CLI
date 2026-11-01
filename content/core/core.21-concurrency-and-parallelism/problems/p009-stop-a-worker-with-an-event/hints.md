## Hint 1

`time.sleep(1.0)` always sleeps the whole second; nothing can wake it early. Which method of
`Event` also waits, but can be woken by `set()` from another thread? What does it return in
each case, and how can you use that return value to leave the loop?

## Hint 2

```
count = 0
while stop is not set:
    tick(); count += 1
    if stop.wait(interval):     # True  -> someone called set(): leave now
        break                   # False -> the interval passed: tick again
return count
```
