## Hint 1

There are two "is it in here?" questions inside the loop: "is `x` in `b`?" and "have I added `x`
already?". Which built-in type answers "is it in here?" in one step, no matter how big it is?
How much does it cost to build one from `b`?

## Hint 2

Build a set from `b` once, before the loop. Keep a second set of what you already added. Keep
the result in a list so the order of `a` is kept.

```
in_b = set(b)
seen = set()
result = []
for x in a:
    if x in in_b and x not in seen:
        seen.add(x); result.append(x)
return result
```
