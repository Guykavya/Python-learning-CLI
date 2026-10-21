## Hint 1

How many members does `x in members` look at when `x` is not a member? How many times does that happen?

## Hint 2

Which built-in collection answers "is x in here?" without looking at every element?

## Hint 3

Build `members = set(...)` once, right after reading line 2. Keep the query loop the same. The set costs
O(n) to build and then each lookup is O(1) on average.
