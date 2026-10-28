## Hint 1

What must the generator remember between two `send` calls? Where do local variables of a generator
live while it is paused? What value should the very first `yield` give?

## Hint 2

One `yield` inside a `while True` loop is enough. It both gives out the current average and
receives the next value. Decide what to do with the received value **after** the `yield`.

## Hint 3

```
total = 0, count = 0, average = None
loop for ever:
    received = yield average
    if received is None: reset total, count, average
    else: add to total, count += 1, average = total / count
```
