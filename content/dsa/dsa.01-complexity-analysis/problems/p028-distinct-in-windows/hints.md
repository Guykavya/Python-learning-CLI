## Hint 1

A set cannot tell you whether a leaving code still has another copy in the block. What could you store instead
of "is this code present"?

## Hint 2

Store how many times each code appears in the current block, in a dict. The number of different codes is the number
of keys whose count is above 0.

## Hint 3

```
fill the dict with the first k codes; answer = number of keys
for i from k to n - 1:
    add 1 to count[a[i]]          (entering)
    subtract 1 from count[a[i-k]] (leaving); if it becomes 0, delete the key
    answer = number of keys
```
