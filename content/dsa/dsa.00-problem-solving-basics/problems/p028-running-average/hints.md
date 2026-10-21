## Hint 1

To compute an average you need the sum and the count. Do you need to remember the individual numbers at all?
And how will your loop know when to stop?

## Hint 2

Read the first number before the loop. Then `while x != 0:` update the total and count, print the average,
and read the next number at the **end** of the loop body. That way the `0` is never added or counted.

## Hint 3

```
total = 0, count = 0
x = read number
while x != 0:
    total = total + x
    count = count + 1
    print f"{total / count:.2f}"
    x = read number
print "count", count
```
