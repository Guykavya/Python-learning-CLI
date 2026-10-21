## Hint 1

If someone reads numbers to you one by one, what do you need to remember to answer the question at the end? What should you remember *before* you have heard any number?

## Hint 2

Starting the largest at 0 fails when every number is negative. Instead, read the first number and use it as both the largest and the smallest so far. Then loop over the remaining `n - 1` numbers.

## Hint 3

```
x = first number
largest = x
smallest = x
repeat n - 1 times:
    x = next number
    if x > largest: largest = x
    if x < smallest: smallest = x
print("max", largest)
print("min", smallest)
```
