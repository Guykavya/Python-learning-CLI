## Hint 1

You need "the next n items" again and again from the **same** source. Why must you call
`iter()` once, before the loop, and not on every round?

## Hint 2

`islice(it, n)` gives at most `n` items from an iterator. If you turn that into a list and it
is empty, what does that tell you about the source?

## Hint 3

```
check n
it = iter(iterable)
loop forever:
    chunk = list(islice(it, n))
    if chunk is empty: stop (return)
    yield chunk
```
