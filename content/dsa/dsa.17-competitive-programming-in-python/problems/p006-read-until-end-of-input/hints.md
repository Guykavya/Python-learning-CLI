## Hint 1

You do not know the number of lines. What object in Python lets you loop until there is nothing left to read? Think `sys.stdin` itself.

## Hint 2

`line.split()` on a blank line, or a line with only spaces, gives `[]`; the sum of an empty list is `0`. It also removes `\r`, so Windows line endings need no special case.

## Hint 3

```text
total = 0
for line in sys.stdin:
    s = sum of ints in line.split()
    print s (collect it)
    total += s
print "total: " + total
```
