## Hint 1

You must stop after `n` items, even if the source could go on for ever. Which loop gives you a natural stopping point, and how do you count?

## Hint 2

Get an iterator with `iter()`. Repeat `n` times: `next(it)` in a `try`; on `StopIteration`, stop early. Do not ask for item `n + 1`.

## Hint 3

```
it = iter(iterable)
result = []
for _ in range(n):
    try: result.append(next(it))
    except StopIteration: break
return result
```
