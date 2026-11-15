## Hint 1

Write `digit_square_sum(n)` first. How do you get the last digit of `n` and remove it (`divmod(n, 10)`)? Check: `digit_square_sum(19)` is `82`.

## Hint 2

Treat `digit_square_sum` as `next`. `slow` takes one step per round, `fast` takes two. Two things can end the walk: `fast` reaches `1` (happy), or `slow == fast` somewhere else (a loop without `1`). Integers are compared with `==`; there are no node objects.

## Hint 3

```
slow = n; fast = next(n)
while fast != 1 and slow != fast:
    slow = next(slow); fast = next(next(fast))
return fast == 1
```
