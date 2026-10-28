## Approach

1. `next(g)` prints `try 5` and yields `10 // 5 = 2`. The main program prints `2`.
2. The second `next(g)` prints `try 0`, then `10 // 0` raises `ZeroDivisionError`. Nothing in
   `risky` catches it, so it leaves the generator. The generator is now **finished**. The main
   program catches the error: `error!`.
3. The third `next(g)` does not continue with `x = 2`. A generator that ended with an error is
   dead, so `next` raises `StopIteration`: `g is finished`. Note: `risky end` never prints.
4. The `for` loop: `try 1`, add 10, `try 0`, error. The error leaves the generator and the
   `for` loop: `loop stopped, total 10`.
5. In `safe` the `try` is inside the loop, so the error never leaves the generator. It yields 2,
   prints `skip 0`, yields 5, then prints `safe end`. `list` collects `[2, 5]`, and only then
   does `print` print the list.

## Output

```text
try 5
2
try 0
error!
g is finished
try 1
try 0
loop stopped, total 10
skip 0
safe end
[2, 5]
```

## Complexity

O(n) for n items.

## Another way

The rule in one line: **an exception that escapes a generator ends it**. If you want a stream that
survives bad items, catch the error *inside* the generator, as `safe` does, or clean the data in an
earlier stage. A generator cannot be "restarted"; you make a new one by calling the function again.
