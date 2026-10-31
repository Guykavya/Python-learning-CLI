## Hint 1

`my_chain` and `my_enumerate` are short `for` loops. Which one-line tool hands over all items of one
iterable? For `my_zip`: how many iterators do you need, and when exactly must the generator stop?

## Hint 2

In `my_zip`, build one row at a time: call `next()` on each iterator in order. If one of them raises
`StopIteration`, the whole generator ends. Inside a generator, end with `return`, never
`raise StopIteration`.

For `my_islice`, count positions. Think about **when** you check the stop: before reading the next
item, not after.

## Hint 3

```
my_zip(*iterables):
    if no iterables: return
    iterators = [iter(x) for x in iterables]
    loop:
        row = []
        for it in iterators:
            try: row.append(next(it))
            except StopIteration: return
        yield tuple(row)

my_islice(iterable, start, stop):
    if stop is not None and stop <= start: return
    position = 0
    for item in iterable:
        if position >= start: yield item
        position += 1
        if stop is not None and position >= stop: return
```
