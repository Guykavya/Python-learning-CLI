## Hint 1

Split the program into four parts and ask one question for each:

1. `f1` and `f2`: what is the difference between `result()` (re-raises) and `exception()`
   (returns)? What does `exception()` give for a job that succeeded? How does `print` show
   `repr()` of an exception?
2. `b` and `q`: at the moment of each `cancel()`, is that job **running** or **waiting in
   the queue**?
3. What does `result()` do on a cancelled future?
4. `map`: does `ex.map(...)` itself raise, or only the loop over its iterator? Which items
   are printed before the failing one?

## Hint 2

Fill in a small table before writing the lines:

```
future   state when asked         call            gives
f1       finished, value 10       result()        10
f1                                exception()     None
f2       finished, ValueError     result()        raises -> except prints message
f2                                exception()     the ValueError object (repr)
b        RUNNING (worker inside)  cancel()        ?
q        PENDING (in the queue)   cancel()        ?
q        cancelled                result()        ?
map      items 1, 2, 3, 4         next(...)       10, 20, then ?
```
