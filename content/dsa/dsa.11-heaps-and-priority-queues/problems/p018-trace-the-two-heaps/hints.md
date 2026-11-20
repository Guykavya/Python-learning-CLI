## Hint 1

Do not simulate the heap arrays. The program prints the halves **sorted**, so you only need to know which numbers are in `low` and which are in `high`. Start with both empty. The first number goes into `low` (step 1), the largest of `low` moves to `high` (step 2), and then `high` has 1 number and `low` has 0. What does step 3 do?

## Hint 2

After every `add` the sizes are `len(low) == len(high)` or `len(low) == len(high) + 1`. Before the add, look at the sizes: if they are equal, then step 2 leaves `high` one bigger and step 3 must run. If `low` was one bigger, step 2 makes them equal and step 3 does nothing. That tells you the note for every line before you move any number.

## Hint 3

Worked state after the first two numbers:

```text
add 7:  step 1: low {7}          step 2: low {}  high {7}      step 3: high bigger -> low {7}  high {}
add 3:  step 1: low {3, 7}       step 2: low {3} high {7}      step 3: sizes equal, nothing
```

Continue with `9`: step 1 gives `low {3, 9}`; step 2 moves `9` to `high`, so `high` is `{7, 9}`, bigger than `low {3}`. What moves back in step 3, and what is the median?
