## Hint 1

Which check must happen before anything else: the type, the right angle, or validity? Why does
"largest side < sum of the other two" only need to be checked for the largest side?

## Hint 2

`largest = max(a, b, c)`. The other two add up to `a + b + c - largest`. For the right-angle test, compare
`largest * largest` with the sum of the other two squares, which is `a*a + b*b + c*c - largest*largest`.
Check equilateral before isosceles, because an equilateral triangle also has two equal sides.

## Hint 3

```
read a, b, c
largest = max(a, b, c)
if any side <= 0 or largest >= a + b + c - largest:
    print "invalid"
else:
    if a == b == c: print "equilateral"
    elif a == b or b == c or a == c: print "isosceles"
    else: print "scalene"
    if a*a + b*b + c*c == 2 * largest * largest: print "right"
    else: print "not right"
```
