## Hint 1

What do you need to remember to know that a key was "already seen"? Which collection gives a fast
`in` test? Where must it be created so two calls do not share it?

## Hint 2

Write a helper generator `clean_words(lines)`: for each line, for each piece of `line.split()`,
`piece.strip(".,!?;:\"'()")`, lower-case it, and yield it if it is not empty. Then `new_words` is
just `unique_by(clean_words(lines))`.

## Hint 3

```
unique_by(iterable, key=None):
    seen = set()
    for item in iterable:
        k = item if key is None else key(item)
        if k not in seen:
            seen.add(k)
            yield item
```
