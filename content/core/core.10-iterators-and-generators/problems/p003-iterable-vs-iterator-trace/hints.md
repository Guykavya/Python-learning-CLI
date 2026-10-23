## Hint 1

A list is an *iterable*: every `iter(nums)` builds a new, independent iterator. `it` is one single iterator. Which of the two keeps a position?

## Hint 2

Write down, for each line, how many items are left in `it`. Remember `iter(nums) is iter(nums)` compares two *new* objects.
