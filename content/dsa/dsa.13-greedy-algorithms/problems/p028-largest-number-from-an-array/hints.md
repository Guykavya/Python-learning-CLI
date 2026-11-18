## Hint 1

Take just two numbers, `a` and `b`, as strings. There are only two ways to place them: `a + b` or `b + a`. Which one should come first? That decides their order in the answer, no matter what else is around them (the rest of the string is the same in both cases).

## Hint 2

Turn that into a comparison function for `sorted` with `functools.cmp_to_key` (dsa.05 section 15): return `-1` when `a + b > b + a` (put `a` first), `1` when it is smaller, `0` when equal. The two strings `a + b` and `b + a` have the same length, so comparing them as text is the same as comparing them as numbers.

## Hint 3

```
strs = [str(x) for x in nums]
sort strs with compare(a, b) = -1 if a+b > b+a, 1 if a+b < b+a, else 0
result = "".join(strs)
if result starts with "0": return "0"      # then every number was 0
return result
```
