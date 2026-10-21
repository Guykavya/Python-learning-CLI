## Hint 1

The slow part is asking "does this value appear anywhere else?" by scanning. Can you instead remember
the values you have already met, in a structure that answers "have I seen this?" instantly?

## Hint 2

A `set` answers `x in s` in O(1) on average, no matter how many items it holds. A list answers it in O(n).

## Hint 3

```
seen = empty set
for each x in the list:
    if x is in seen: answer YES, stop
    add x to seen
if never stopped: answer NO
```
