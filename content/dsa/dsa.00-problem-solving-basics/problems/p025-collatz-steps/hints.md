## Hint 1

What should the loop condition be: when do you stop? What are the "step counter" and the "largest so far" before any step has happened?

## Hint 2

Start `steps = 0` and `peak = n`. While `n != 1`: change `n` by the rule, add 1 to `steps`, and update `peak` if the new `n` is bigger.
Halve with `//`, not `/`: `/` turns the number into a float, which prints with `.0` and loses digits once numbers get huge.

## Hint 3

```
read n
steps = 0
peak = n
while n != 1:
    if n % 2 == 0: n = n // 2
    else: n = 3 * n + 1
    steps = steps + 1
    if n > peak: peak = n
print "steps", steps
print "peak", peak
```
