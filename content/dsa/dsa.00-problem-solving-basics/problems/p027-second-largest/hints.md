## Hint 1

You need two variables: the largest so far and the second largest so far. What should "second largest so far"
be before you have seen two different values? How will your program know it does not exist yet?

## Hint 2

Read the first number into `first`. Keep `second` and a flag `has_second = False`.
For each later number `x`: if `x > first`, the old `first` becomes `second`, and `x` becomes `first`.
Otherwise, if `x < first` and (there is no second yet, or `x > second`), then `x` becomes `second`.
If `x == first`, do nothing.

## Hint 3

```
read n
first = next number
has_second = False, second = 0
repeat n - 1 times:
    x = next number
    if x > first:
        second = first, has_second = True, first = x
    elif x < first and (not has_second or x > second):
        second = x, has_second = True
print second if has_second else "none"
```
