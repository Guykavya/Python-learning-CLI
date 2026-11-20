## Hint 1

Forget the right neighbours for a moment. If only the rule "more than my **left** neighbour when my rating is higher" existed, what is the fewest candies for each child, going from left to right? Write it down for `[1, 3, 4, 5, 2]`: `left = [1, 2, 3, 4, 1]`.

## Hint 2

Do the same from the right: `right[i]` is the fewest candies when only the "more than my **right** neighbour" rule exists, filled from right to left. For `[1, 3, 4, 5, 2]`: `right = [1, 1, 1, 2, 1]`. A child must obey both rules, so it needs at least `max(left[i], right[i])`. Is that also enough? Check child 3: `max(4, 2) = 4` beats both neighbours.

## Hint 3

You can do it with one list: fill it left to right, then sweep right to left and only ever **raise** a value.

```
c = [1] * n
for i in 1 .. n-1:
    if ratings[i] > ratings[i-1]: c[i] = c[i-1] + 1
for i in n-2 down to 0:
    if ratings[i] > ratings[i+1]: c[i] = max(c[i], c[i+1] + 1)
return sum(c)
```

Why `max` in the second pass: a peak like the 5 in `[1, 3, 4, 5, 2]` already has 4 from the left pass. The right pass only asks for 2. Writing `c[i] = c[i+1] + 1` would lower it to 2 and break the rule with its left neighbour (4 has 3 candies).
